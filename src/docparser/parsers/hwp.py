"""HWP v5 binary format parser.

Parses the OLE2-based HWP binary format according to Hancom's
"HWP Binary Specification 1.1".

Pipeline:
    OLE2 file → decompress sections → parse binary records → extract elements → Document
"""

from __future__ import annotations

import struct
import zlib
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path

import olefile

from ..models import Document, Metadata, Paragraph, Table, TableCell, TableRow

# ---------------------------------------------------------------------------
# Record header bit layout
# ---------------------------------------------------------------------------
# A record header is a 4-byte (uint32 LE) value:
#   [tag_id: 10 bits][level: 10 bits][size: 12 bits]
# If size == 0xFFF (EXTENDED_SIZE_SENTINEL), the next 4 bytes hold the real size.

TAG_BITS = 10
LEVEL_BITS = 10

TAG_MASK = (1 << TAG_BITS) - 1  # 0x3FF
LEVEL_MASK = (1 << LEVEL_BITS) - 1  # 0x3FF
SIZE_MASK = (1 << 12) - 1  # 0xFFF
EXTENDED_SIZE_SENTINEL = SIZE_MASK  # 0xFFF — "real size in next 4 bytes"

# ---------------------------------------------------------------------------
# HWP tag IDs  (HWPTAG_BEGIN = 16)
# ---------------------------------------------------------------------------
HWPTAG_PARA_HEADER = 66
HWPTAG_PARA_TEXT = 67
HWPTAG_CTRL_HEADER = 71
HWPTAG_LIST_HEADER = 72
HWPTAG_TABLE = 77  # HWPTAG_BEGIN + 61

# ---------------------------------------------------------------------------
# Control type ID — HWP stores ctrl IDs byte-reversed:
# 'tbl ' as bytes [0x20, 0x6c, 0x62, 0x74].
# Reading LE gives 0x74626c20 == struct.unpack(">I", b"tbl ").
# ---------------------------------------------------------------------------
CTRL_TABLE_ID = struct.unpack(">I", b"tbl ")[0]  # 0x74626c20

# ---------------------------------------------------------------------------
# PARA_TEXT character codes
# ---------------------------------------------------------------------------
# Extended control characters occupy 8 uint16 = 16 bytes total.
EXTENDED_CTRL_CHARS = frozenset(range(0, 9)) | {11, 12} | frozenset(range(14, 24))
EXTENDED_CTRL_SIZE = 16  # bytes (8 × uint16)

CHAR_TAB = 9
CHAR_LINE_BREAK = 10
CHAR_TABLE_OBJECT = 11  # GSO (table, image 등) marker
CHAR_PARAGRAPH_END = 13
PRINTABLE_THRESHOLD = 32


# ---------------------------------------------------------------------------
# Low-level data structures
# ---------------------------------------------------------------------------
@dataclass(slots=True)
class Record:
    """A single parsed HWP binary record."""

    tag: int
    level: int
    data: bytes


@dataclass(slots=True)
class CharInfo:
    """Character information extracted from PARA_TEXT bytes."""

    code: int  # uint16 character code
    offset: int  # byte offset within PARA_TEXT data
    size: int  # bytes consumed by this character (2 or 16)


# ---------------------------------------------------------------------------
# Character scanning utilities
# ---------------------------------------------------------------------------
def _is_extended_ctrl(code: int) -> bool:
    """확장 제어문자인지 판별 (16바이트 점유)."""
    return code in EXTENDED_CTRL_CHARS


def scan_para_chars(data: bytes) -> Iterator[CharInfo]:
    """HWPTAG_PARA_TEXT 바이트를 순회하며 CharInfo를 yield한다.

    확장 제어문자(16바이트)와 일반 문자(2바이트)를 올바르게 구분한다.
    """
    offset = 0
    length = len(data)
    while offset + 1 < length:
        code = struct.unpack_from("<H", data, offset)[0]
        if _is_extended_ctrl(code):
            yield CharInfo(code=code, offset=offset, size=EXTENDED_CTRL_SIZE)
            offset += EXTENDED_CTRL_SIZE
        else:
            yield CharInfo(code=code, offset=offset, size=2)
            offset += 2


def extract_text(data: bytes) -> str:
    """PARA_TEXT 바이트에서 사람이 읽을 수 있는 텍스트를 추출한다."""
    chars: list[str] = []
    for info in scan_para_chars(data):
        if info.code == CHAR_TAB:
            chars.append("\t")
        elif info.code == CHAR_LINE_BREAK:
            chars.append("\n")
        elif info.code >= PRINTABLE_THRESHOLD:
            chars.append(chr(info.code))
    return "".join(chars)


def has_table_marker(data: bytes) -> bool:
    """파라그래프에 테이블/GSO 마커(char 11)가 있는지 확인한다."""
    return any(info.code == CHAR_TABLE_OBJECT for info in scan_para_chars(data))


# ---------------------------------------------------------------------------
# Record cursor — explicit traversal over a record list
# ---------------------------------------------------------------------------
class RecordCursor:
    """레코드 리스트를 순회하는 커서."""

    def __init__(self, records: list[Record], start: int = 0) -> None:
        self._records = records
        self._pos = start

    @property
    def pos(self) -> int:
        return self._pos

    @pos.setter
    def pos(self, value: int) -> None:
        self._pos = value

    def has_next(self) -> bool:
        return self._pos < len(self._records)

    def peek(self) -> Record | None:
        return self._records[self._pos] if self.has_next() else None

    def advance(self) -> Record:
        rec = self._records[self._pos]
        self._pos += 1
        return rec


# ---------------------------------------------------------------------------
# Record stream parsing
# ---------------------------------------------------------------------------
def _parse_records(data: bytes) -> list[Record]:
    """바이너리 레코드 스트림을 Record 리스트로 파싱한다."""
    records: list[Record] = []
    offset = 0
    data_len = len(data)

    while offset + 4 <= data_len:
        header = struct.unpack_from("<I", data, offset)[0]
        tag = header & TAG_MASK
        level = (header >> TAG_BITS) & LEVEL_MASK
        size = (header >> (TAG_BITS + LEVEL_BITS)) & SIZE_MASK
        offset += 4

        if size == EXTENDED_SIZE_SENTINEL:
            if offset + 4 > data_len:
                break
            size = struct.unpack_from("<I", data, offset)[0]
            offset += 4

        if offset + size > data_len:
            break

        records.append(Record(tag=tag, level=level, data=data[offset : offset + size]))
        offset += size

    return records


# ---------------------------------------------------------------------------
# FileHeader utilities
# ---------------------------------------------------------------------------
def _check_compressed(ole: olefile.OleFileIO) -> bool:
    """HWP 문서 본문이 압축되어 있는지 확인한다."""
    header = ole.openstream("FileHeader").read()
    if len(header) > 36:
        return bool(header[36] & 0x01)
    return False


def _read_ctrl_id(data: bytes) -> int:
    """CTRL_HEADER 데이터에서 컨트롤 타입 ID(uint32 LE)를 읽는다."""
    if len(data) >= 4:
        return struct.unpack_from("<I", data, 0)[0]
    return 0


# ---------------------------------------------------------------------------
# Table parsing — split into 3 phases
# ---------------------------------------------------------------------------
def _find_table_ctrl(cursor: RecordCursor, para_level: int) -> int | None:
    """Phase 1: CTRL_HEADER(tbl) 레코드를 찾아 ctrl_level을 반환한다.

    테이블이 아니거나 다음 문단에 도달하면 None을 반환한다.
    """
    while cursor.has_next():
        rec = cursor.peek()
        assert rec is not None
        if rec.tag == HWPTAG_CTRL_HEADER and len(rec.data) >= 4:
            ctrl_id = _read_ctrl_id(rec.data)
            if ctrl_id == CTRL_TABLE_ID:
                ctrl_level = rec.level
                cursor.advance()
                return ctrl_level
        # 같은/상위 레벨의 다음 문단을 만나면 중단
        if rec.tag == HWPTAG_PARA_HEADER and rec.level <= para_level:
            return None
        cursor.advance()
    return None


def _read_table_dimensions(cursor: RecordCursor) -> tuple[int, int]:
    """Phase 2: HWPTAG_TABLE 레코드에서 (n_rows, n_cols)를 읽는다."""
    rec = cursor.peek()
    if rec is not None and rec.tag == HWPTAG_TABLE:
        tbl_data = rec.data
        cursor.advance()
        if len(tbl_data) >= 8:
            n_rows = struct.unpack_from("<H", tbl_data, 4)[0]
            n_cols = struct.unpack_from("<H", tbl_data, 6)[0]
            return n_rows, n_cols
    return 0, 0


def _collect_table_cells(
    cursor: RecordCursor, ctrl_level: int, n_rows: int, n_cols: int
) -> Table:
    """Phase 3: LIST_HEADER + PARA_TEXT에서 셀 텍스트를 수집하여 Table을 빌드한다."""
    cell_texts: list[str] = []
    current_cell_parts: list[str] = []
    in_cell = False

    while cursor.has_next():
        rec = cursor.peek()
        assert rec is not None

        # 테이블 종료: ctrl_level 이하 레벨의 PARA_HEADER를 만남
        if rec.level <= ctrl_level and rec.tag == HWPTAG_PARA_HEADER:
            if in_cell:
                cell_texts.append("\n".join(current_cell_parts))
            break

        if rec.tag == HWPTAG_LIST_HEADER and rec.level == ctrl_level + 1:
            # 새 셀 시작
            if in_cell:
                cell_texts.append("\n".join(current_cell_parts))
            current_cell_parts = []
            in_cell = True

        elif rec.tag == HWPTAG_PARA_TEXT and in_cell:
            text = extract_text(rec.data).strip()
            if text:
                current_cell_parts.append(text)

        cursor.advance()
    else:
        # 레코드 끝까지 도달
        if in_cell:
            cell_texts.append("\n".join(current_cell_parts))

    # 수집된 셀 텍스트로 Table 객체 생성
    table = Table()
    cell_idx = 0
    for _ in range(n_rows):
        row = TableRow()
        for _ in range(n_cols):
            cell = TableCell()
            if cell_idx < len(cell_texts):
                text = cell_texts[cell_idx]
                if text:
                    cell.paragraphs.append(Paragraph(text=text))
            row.cells.append(cell)
            cell_idx += 1
        table.rows.append(row)

    return table


def _try_parse_table(cursor: RecordCursor, para_level: int) -> Table | None:
    """테이블 파싱을 시도한다. 실패 시 None을 반환한다."""
    # Phase 1: 테이블 컨트롤 헤더 탐색
    ctrl_level = _find_table_ctrl(cursor, para_level)
    if ctrl_level is None:
        return None

    # Phase 2: 테이블 차원(행/열 수) 읽기
    n_rows, n_cols = _read_table_dimensions(cursor)
    if n_rows == 0 or n_cols == 0:
        return None

    # Phase 3: 셀 텍스트 수집 + Table 객체 빌드
    return _collect_table_cells(cursor, ctrl_level, n_rows, n_cols)


# ---------------------------------------------------------------------------
# Element extraction
# ---------------------------------------------------------------------------
def _extract_elements(records: list[Record]) -> list[Paragraph | Table]:
    """레코드 시퀀스에서 문서 요소(Paragraph, Table)를 추출한다."""
    elements: list[Paragraph | Table] = []
    cursor = RecordCursor(records)

    while cursor.has_next():
        rec = cursor.peek()
        assert rec is not None

        # 테이블 마커가 있는 문단 처리
        if rec.tag == HWPTAG_PARA_TEXT and has_table_marker(rec.data):
            para_level = rec.level
            cursor.advance()  # 현재 PARA_TEXT를 소비
            table = _try_parse_table(cursor, para_level)
            if table and table.rows:
                # 1×1 래퍼 테이블 → 일반 문단으로 풀어냄
                if len(table.rows) == 1 and len(table.rows[0].cells) == 1:
                    cell = table.rows[0].cells[0]
                    for p in cell.paragraphs:
                        if p.text.strip():
                            elements.append(Paragraph(text=p.text.strip()))
                else:
                    elements.append(table)
                continue

        if rec.tag == HWPTAG_PARA_TEXT:
            text = extract_text(rec.data)
            stripped = text.strip()
            if stripped:
                elements.append(Paragraph(text=stripped))

        cursor.advance()

    return elements


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------
def parse_hwp(filepath: str | Path) -> Document:
    """HWP v5 바이너리 파일을 파싱하여 Document를 반환한다."""
    ole = olefile.OleFileIO(str(filepath))
    try:
        is_compressed = _check_compressed(ole)
        doc = Document(metadata=Metadata(source_format="hwp"))

        section_idx = 0
        while True:
            stream_name = f"BodyText/Section{section_idx}"
            if not ole.exists(stream_name):
                break

            raw = ole.openstream(stream_name).read()
            if is_compressed:
                raw = zlib.decompress(raw, -15)

            records = _parse_records(raw)
            elements = _extract_elements(records)
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
    finally:
        ole.close()


class HwpParser:
    """HWP v5 parser — Parser protocol implementation."""

    @staticmethod
    def extensions() -> list[str]:
        return [".hwp"]

    @staticmethod
    def parse(filepath: Path | str) -> Document:
        return parse_hwp(filepath)
