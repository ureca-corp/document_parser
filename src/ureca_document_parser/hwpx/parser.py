"""HWPX format parser.

HWPX is a ZIP-based Open Packaging Convention (OPC) format containing
XML files that describe the document structure. This parser extracts
text, tables, and heading information from the XML sections.

Pipeline:
    ZIP archive → find section XMLs → parse XML → extract elements → Document
"""

from __future__ import annotations

import zipfile
from collections.abc import Iterator
from pathlib import Path
from xml.etree import ElementTree as ET

from ..models import (
    Document,
    Metadata,
    Paragraph,
    ParseError,
    Table,
    TableCell,
    TableRow,
)
from ..styles import HEADING_STYLE_PATTERNS


# ---------------------------------------------------------------------------
# XML namespace utilities
# ---------------------------------------------------------------------------
def _strip_ns(tag: str) -> str:
    """'{namespace}localname' → 'localname'."""
    return tag.rsplit("}", 1)[-1] if "}" in tag else tag


def _children(parent: ET.Element, local_name: str) -> Iterator[ET.Element]:
    """네임스페이스 무관하게 직계 자식 중 local_name과 일치하는 요소를 yield한다."""
    return (ch for ch in parent if _strip_ns(ch.tag) == local_name)


def _find_children(parent: ET.Element, local_name: str) -> list[ET.Element]:
    """직계 자식 중 local_name과 일치하는 요소를 리스트로 반환한다."""
    return [ch for ch in parent if _strip_ns(ch.tag) == local_name]


# ---------------------------------------------------------------------------
# Section file discovery
# ---------------------------------------------------------------------------
def _find_section_files(zf: zipfile.ZipFile) -> list[str]:
    """HWPX 아카이브에서 섹션 XML 파일 목록을 찾는다."""
    names = zf.namelist()

    # content.hpf 매니페스트에서 섹션 순서 읽기 시도
    for manifest in ("Contents/content.hpf", "contents/content.hpf"):
        if manifest in names:
            try:
                sections = _parse_manifest(zf.read(manifest))
                if sections:
                    return sections
            except Exception:
                pass

    # 폴백: 파일명 패턴으로 섹션 파일 탐색
    return sorted(n for n in names if _is_section_file(n))


def _is_section_file(name: str) -> bool:
    """파일명이 섹션 XML 파일 패턴과 일치하는지 확인한다."""
    lower = name.lower()
    return ("section" in lower and lower.endswith(".xml")) or (
        "contents/" in lower and "section" in lower
    )


def _parse_manifest(data: bytes) -> list[str]:
    """content.hpf 매니페스트를 파싱하여 정렬된 섹션 파일 목록을 반환한다."""
    root = ET.fromstring(data)
    sections: list[str] = []

    for elem in root.iter():
        href = elem.get("href", "")
        if "section" in href.lower() and href.endswith(".xml"):
            if not href.startswith("Contents/"):
                href = "Contents/" + href
            sections.append(href)

    return sections


# ---------------------------------------------------------------------------
# XML element processing
# ---------------------------------------------------------------------------
def _process_element(element: ET.Element, elements: list[Paragraph | Table]) -> None:
    """XML 요소를 재귀적으로 처리하여 Paragraph와 Table을 추출한다."""
    tag = _strip_ns(element.tag)

    if tag == "tbl":
        table = _parse_table_element(element)
        if table and table.rows:
            elements.append(table)
        return

    if tag == "p":
        para = _parse_paragraph_element(element)
        if para and para.text.strip():
            elements.append(para)
        # 문단 내부의 서브 테이블도 처리
        for child in element:
            if _strip_ns(child.tag) in ("tbl", "subList"):
                _process_element(child, elements)
        return

    # 기타 컨테이너 요소는 재귀 탐색
    for child in element:
        _process_element(child, elements)


# ---------------------------------------------------------------------------
# Paragraph parsing
# ---------------------------------------------------------------------------
def _parse_paragraph_element(p_elem: ET.Element) -> Paragraph | None:
    """<p> 요소를 Paragraph로 파싱한다."""
    texts: list[str] = []

    # <run>/<t> 요소에서 텍스트 추출
    for run in _find_children(p_elem, "run"):
        for t in _find_children(run, "t"):
            if t.text:
                texts.append(t.text)
            if t.tail:
                texts.append(t.tail)

    # 일부 HWPX 변형에서 직접 <t> 요소가 존재
    for t in _find_children(p_elem, "t"):
        if t.text and t.text not in texts:
            texts.append(t.text)

    text = "".join(texts)
    if not text.strip():
        return None

    heading_level = _detect_heading_level(p_elem)
    return Paragraph(text=text.strip(), heading_level=heading_level)


def _detect_heading_level(p_elem: ET.Element) -> int:
    """문단 속성에서 제목 레벨을 감지한다."""
    # pPr (paragraph properties)의 outlineLevel 확인
    for ppr in _find_children(p_elem, "pPr"):
        outline = ppr.get("outlineLevel")
        if outline is not None:
            try:
                level = int(outline)
                if 1 <= level <= 6:
                    return level
            except ValueError:
                pass

    # 스타일 ID 패턴 확인
    style_id = p_elem.get("styleIDRef", "")
    if not style_id:
        for ppr in _find_children(p_elem, "pPr"):
            style_id = ppr.get("styleIDRef", "")

    style_lower = style_id.lower()
    for pattern, level in HEADING_STYLE_PATTERNS.items():
        if pattern in style_lower:
            return level

    return 0


# ---------------------------------------------------------------------------
# Table parsing
# ---------------------------------------------------------------------------
def _parse_table_element(tbl_elem: ET.Element) -> Table:
    """<tbl> 요소를 Table로 파싱한다."""
    table = Table()

    for tr in _children(tbl_elem, "tr"):
        row = TableRow()
        for tc in _children(tr, "tc"):
            cell = _parse_table_cell(tc)
            row.cells.append(cell)
        if row.cells:
            table.rows.append(row)

    return table


def _parse_table_cell(tc_elem: ET.Element) -> TableCell:
    """<tc> 요소를 TableCell로 파싱한다. 중첩 테이블도 지원."""
    cell = TableCell()

    for child in tc_elem:
        tag = _strip_ns(child)
        if tag == "p":
            para = _parse_paragraph_element(child)
            if para:
                cell.content.append(para)
            # 문단 내부 중첩 테이블
            for p_child in child:
                if _strip_ns(p_child) == "tbl":
                    nested = _parse_table_element(p_child)
                    if nested and nested.rows:
                        cell.content.append(nested)
        elif tag == "tbl":
            nested = _parse_table_element(child)
            if nested and nested.rows:
                cell.content.append(nested)
        elif tag == "subList":
            for sub_child in child:
                sub_tag = _strip_ns(sub_child)
                if sub_tag == "p":
                    para = _parse_paragraph_element(sub_child)
                    if para:
                        cell.content.append(para)
                elif sub_tag == "tbl":
                    nested = _parse_table_element(sub_child)
                    if nested and nested.rows:
                        cell.content.append(nested)

    return cell


# ---------------------------------------------------------------------------
# Section XML parsing
# ---------------------------------------------------------------------------
def _parse_section_xml(xml_data: bytes) -> list[Paragraph | Table]:
    """섹션 XML을 파싱하여 문서 요소 리스트를 반환한다."""
    elements: list[Paragraph | Table] = []
    root = ET.fromstring(xml_data)
    _process_element(root, elements)
    return elements


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------
def parse_hwpx(filepath: str | Path) -> Document:
    """HWPX 파일을 파싱하여 Document를 반환한다."""
    path = Path(filepath)
    if not path.exists():
        raise ParseError(f"파일을 찾을 수 없습니다: {path}")

    doc = Document(metadata=Metadata(source_format="hwpx"))

    try:
        zf = zipfile.ZipFile(str(path), "r")
    except (zipfile.BadZipFile, Exception) as e:
        raise ParseError(f"유효한 HWPX 파일이 아닙니다: {path}") from e
    with zf:
        section_files = _find_section_files(zf)
        for section_file in section_files:
            xml_data = zf.read(section_file)
            elements = _parse_section_xml(xml_data)
            doc.elements.extend(elements)

    return doc


class HwpxParser:
    """HWPX parser — Parser protocol implementation."""

    @staticmethod
    def extensions() -> list[str]:
        return [".hwpx"]

    @staticmethod
    def parse(filepath: Path | str) -> Document:
        return parse_hwpx(filepath)
