"""HWP v5 binary format parser.

Parses the OLE2-based HWP binary format according to Hancom's
"HWP Binary Specification 1.1".

Pipeline:
    OLE2 file → decompress sections → parse binary records → extract elements → Document
"""

from __future__ import annotations

import struct
import zlib
from pathlib import Path

import olefile

from ..models import Document, Metadata, Paragraph, ParseError, Table
from ..styles import heading_level_from_style
from .records import (
    HWPTAG_PARA_HEADER,
    HWPTAG_PARA_TEXT,
    HWPTAG_STYLE,
    RecordCursor,
    parse_records,
)
from .tables import try_parse_table
from .text import extract_text, has_table_marker, read_bstr


# ---------------------------------------------------------------------------
# FileHeader utilities
# ---------------------------------------------------------------------------
def _check_compressed(ole: olefile.OleFileIO) -> bool:
    """HWP 문서 본문이 압축되어 있는지 확인한다."""
    header = ole.openstream("FileHeader").read()
    if len(header) > 36:
        return bool(header[36] & 0x01)
    return False


# ---------------------------------------------------------------------------
# DocInfo stream — style table extraction
# ---------------------------------------------------------------------------
def _parse_styles(ole: olefile.OleFileIO, is_compressed: bool) -> list[int]:
    """DocInfo 스트림에서 스타일 테이블을 파싱하여 heading_level 매핑을 반환.

    Returns a list where index == style_id, value == heading_level (0 = normal).
    """
    if not ole.exists("DocInfo"):
        return []

    raw = ole.openstream("DocInfo").read()
    if is_compressed:
        try:
            raw = zlib.decompress(raw, -15)
        except zlib.error:
            return []

    records = parse_records(raw)
    style_levels: list[int] = []
    for rec in records:
        if rec.tag != HWPTAG_STYLE:
            continue
        local_name, offset = read_bstr(rec.data, 0)
        english_name, _ = read_bstr(rec.data, offset)
        level = heading_level_from_style(local_name) or heading_level_from_style(
            english_name
        )
        style_levels.append(level)

    return style_levels


def _read_para_style_id(data: bytes) -> int:
    """HWPTAG_PARA_HEADER 데이터에서 style_id(UINT16, offset 4)를 읽는다."""
    if len(data) >= 6:
        return struct.unpack_from("<H", data, 4)[0]
    return 0


# ---------------------------------------------------------------------------
# Section-header table detection
# ---------------------------------------------------------------------------
# 한국 공공기관 HWP 문서에서 섹션 제목을 표(Table)로 꾸미는 패턴을 감지하여
# Heading Paragraph로 변환한다.
#
# 감지 패턴:
#   2행 이하, 4열, 첫 행 = [번호, 빈칸, 제목, 빈칸], 나머지 행 비어있음
#   예: | 1 |  | 사업개요 |  |  →  ## 1. 사업개요
#
# 오탐(false positive) 발생 시 대응 방법:
#   - 실제 데이터 테이블이 위 패턴과 우연히 일치하여 heading으로 변환되는 경우
#     → 조건을 더 엄격하게 강화 (예: 열 수 제한, 번호 범위 제한 등)
#
# 미탐(false negative) 발생 시 대응 방법:
#   - 열 수가 4가 아닌 섹션 헤더 (예: 3열, 2열 구성)
#     → first_row.cells 길이 조건을 완화하거나 별도 분기 추가
#   - 번호가 숫자가 아닌 경우 (예: "Ⅰ", "Ⅱ", "가", "나", "제1조")
#     → num_text.isdigit() 대신 정규식 또는 허용 패턴 목록으로 교체
#   - 빈칸 셀에 공백/특수문자가 들어있는 경우
#     → _cell_text의 strip 로직 점검
#   - 2번째 행에 부제목 등 텍스트가 있는 변형 패턴
#     → 2행 비어있음 검사를 완화하고, 부제목을 heading에 포함하도록 확장
# ---------------------------------------------------------------------------


def _cell_text(cell) -> str:
    """TableCell에서 텍스트를 추출한다."""
    return " ".join(
        p.text for p in cell.content if isinstance(p, Paragraph) and p.text.strip()
    ).strip()


def _try_extract_section_heading(table: Table) -> Paragraph | None:
    """목차형 섹션 헤더 테이블을 Heading Paragraph로 변환한다.

    Returns None if the table does not match the section-header pattern,
    leaving it to be rendered as a normal table.
    """
    if not table.rows or len(table.rows) > 2:
        return None
    first_row = table.rows[0]
    if len(first_row.cells) != 4:
        return None

    num_text = _cell_text(first_row.cells[0])
    gap1 = _cell_text(first_row.cells[1])
    title_text = _cell_text(first_row.cells[2])
    gap2 = _cell_text(first_row.cells[3])

    if not num_text.isdigit() or gap1 or not title_text or gap2:
        return None

    if len(table.rows) == 2 and any(_cell_text(c) for c in table.rows[1].cells):
        return None

    return Paragraph(text=f"{num_text}. {title_text}", heading_level=2)


# ---------------------------------------------------------------------------
# Element extraction
# ---------------------------------------------------------------------------
def _extract_elements(
    records: list, style_levels: list[int] | None = None
) -> list[Paragraph | Table]:
    """레코드 시퀀스에서 문서 요소(Paragraph, Table)를 추출한다."""
    elements: list[Paragraph | Table] = []
    cursor = RecordCursor(records)
    current_heading_level = 0

    while cursor.has_next():
        rec = cursor.peek()
        if rec is None:
            break

        if rec.tag == HWPTAG_PARA_HEADER:
            current_heading_level = 0
            if style_levels:
                sid = _read_para_style_id(rec.data)
                if 0 <= sid < len(style_levels):
                    current_heading_level = style_levels[sid]
            cursor.advance()
            continue

        if rec.tag == HWPTAG_PARA_TEXT and has_table_marker(rec.data):
            para_level = rec.level
            cursor.advance()
            table = try_parse_table(cursor, para_level)
            if table and table.rows:
                # 섹션 헤더 테이블 감지: [번호 | 빈칸 | 제목 | 빈칸] + 빈 행
                heading = _try_extract_section_heading(table)
                if heading:
                    elements.append(heading)
                elif len(table.rows) == 1 and len(table.rows[0].cells) == 1:
                    cell = table.rows[0].cells[0]
                    for item in cell.content:
                        if isinstance(item, Paragraph) and item.text.strip():
                            elements.append(Paragraph(text=item.text.strip()))
                        elif isinstance(item, Table):
                            elements.append(item)
                else:
                    elements.append(table)
                continue

        if rec.tag == HWPTAG_PARA_TEXT:
            text = extract_text(rec.data)
            stripped = text.strip()
            if stripped:
                elements.append(
                    Paragraph(text=stripped, heading_level=current_heading_level)
                )

        cursor.advance()

    return elements


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------
def parse_hwp(filepath: str | Path) -> Document:
    """HWP v5 바이너리 파일을 파싱하여 Document를 반환한다."""
    path = Path(filepath)
    if not path.exists():
        raise ParseError(f"파일을 찾을 수 없습니다: {path}")
    try:
        ole = olefile.OleFileIO(str(path))
    except Exception as e:
        raise ParseError(f"유효한 HWP 파일이 아닙니다: {path}") from e
    with ole:
        is_compressed = _check_compressed(ole)
        style_levels = _parse_styles(ole, is_compressed)
        doc = Document(metadata=Metadata(source_format="hwp"))

        section_idx = 0
        while True:
            stream_name = f"BodyText/Section{section_idx}"
            if not ole.exists(stream_name):
                break

            raw = ole.openstream(stream_name).read()
            if is_compressed:
                raw = zlib.decompress(raw, -15)

            records = parse_records(raw)
            elements = _extract_elements(records, style_levels)
            doc.elements.extend(elements)
            section_idx += 1

        # 폴백: BodyText에서 추출 실패 시 PrvText 사용
        if not doc.elements and ole.exists("PrvText"):
            text = ole.openstream("PrvText").read().decode("utf-16-le", errors="ignore")
            for line in text.split("\r\n"):
                stripped = line.strip()
                if stripped:
                    doc.elements.append(Paragraph(text=stripped))

        return doc


class HwpParser:
    """HWP v5 parser — Parser protocol implementation."""

    @staticmethod
    def extensions() -> list[str]:
        return [".hwp"]

    @staticmethod
    def parse(filepath: Path | str) -> Document:
        return parse_hwp(filepath)
