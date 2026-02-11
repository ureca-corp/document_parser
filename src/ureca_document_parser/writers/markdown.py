"""Markdown writer — converts Document model to Markdown format."""

from __future__ import annotations

from ..models import (
    Document,
    HorizontalRule,
    Image,
    Link,
    ListItem,
    Paragraph,
    Table,
    TableCell,
)


def to_markdown(doc: Document) -> str:
    """Document를 Markdown 문자열로 변환한다."""
    blocks: list[str] = []
    i = 0
    elements = doc.elements

    while i < len(elements):
        element = elements[i]

        if isinstance(element, ListItem):
            # 연속 ListItem을 하나의 블록으로 그룹핑
            list_lines: list[str] = []
            ordered_counter = 0
            while i < len(elements) and isinstance(elements[i], ListItem):
                item = elements[i]
                if item.ordered:
                    ordered_counter += 1
                else:
                    ordered_counter = 0
                list_lines.append(_render_list_item(item, ordered_counter))
                i += 1
            blocks.append("\n".join(list_lines))
        elif isinstance(element, Paragraph):
            blocks.append(_render_paragraph(element))
            i += 1
        elif isinstance(element, Table):
            rendered = _render_table(element)
            if rendered:
                blocks.append(rendered)
            i += 1
        elif isinstance(element, Image):
            blocks.append(_render_image(element))
            i += 1
        elif isinstance(element, Link):
            blocks.append(_render_link(element))
            i += 1
        elif isinstance(element, HorizontalRule):
            blocks.append("---")
            i += 1
        else:
            i += 1

    return "\n\n".join(blocks) + "\n"


def _render_paragraph(para: Paragraph) -> str:
    """Paragraph를 Markdown으로 렌더링한다."""
    text = para.text
    if para.heading_level > 0:
        prefix = "#" * para.heading_level
        return f"{prefix} {text}"
    return text


def _render_cell_content(cell: TableCell) -> str:
    """셀 내용을 문자열로 렌더링한다. 중첩 표는 HTML table로 변환."""
    parts: list[str] = []
    for item in cell.content:
        if isinstance(item, Paragraph) and item.text:
            parts.append(item.text)
        elif isinstance(item, Table):
            parts.append(_render_nested_table_html(item))
    text = "<br>".join(parts)
    text = text.replace("\n", "<br>")
    text = text.replace("|", "\\|")
    return text


def _render_nested_table_html(table: Table) -> str:
    """중첩 표를 인라인 HTML <table>로 렌더링한다."""
    lines: list[str] = ["<table>"]
    for row in table.rows:
        lines.append("<tr>")
        for cell in row.cells:
            cell_html = _render_cell_content(cell).replace("<br>", " ")
            lines.append(f"<td>{cell_html}</td>")
        lines.append("</tr>")
    lines.append("</table>")
    return "".join(lines)


def _render_table(table: Table) -> str:
    """Table을 Markdown 파이프 테이블로 렌더링한다."""
    if not table.rows:
        return ""

    n_cols = max(len(row.cells) for row in table.rows)
    if n_cols == 0:
        return ""

    # 셀 텍스트 매트릭스 생성
    matrix: list[list[str]] = []
    for row in table.rows:
        row_texts: list[str] = []
        for i in range(n_cols):
            if i < len(row.cells):
                row_texts.append(_render_cell_content(row.cells[i]))
            else:
                row_texts.append("")
        matrix.append(row_texts)

    # 열 너비 계산
    col_widths = [3] * n_cols
    for row_texts in matrix:
        for i, text in enumerate(row_texts):
            col_widths[i] = max(col_widths[i], len(text))

    # 헤더 행 (첫 행)
    lines: list[str] = []
    header = matrix[0]
    lines.append(
        "| " + " | ".join(h.ljust(col_widths[i]) for i, h in enumerate(header)) + " |"
    )

    # 구분자 행
    lines.append("| " + " | ".join("-" * col_widths[i] for i in range(n_cols)) + " |")

    # 데이터 행
    for row_texts in matrix[1:]:
        lines.append(
            "| "
            + " | ".join(t.ljust(col_widths[i]) for i, t in enumerate(row_texts))
            + " |"
        )

    return "\n".join(lines)


def _render_image(image: Image) -> str:
    """Image를 Markdown으로 렌더링한다."""
    alt = image.alt_text or "image"
    if image.source:
        return f"![{alt}]({image.source})"
    return f"![{alt}]()"


def _render_list_item(item: ListItem, counter: int = 0) -> str:
    """ListItem을 Markdown으로 렌더링한다."""
    indent = "  " * item.level
    marker = f"{counter}." if item.ordered else "-"
    return f"{indent}{marker} {item.text}"


def _render_link(link: Link) -> str:
    """Link를 Markdown으로 렌더링한다."""
    return f"[{link.text}]({link.url})"


class MarkdownWriter:
    """Markdown writer — Writer protocol implementation."""

    @staticmethod
    def format_name() -> str:
        return "markdown"

    @staticmethod
    def file_extension() -> str:
        return ".md"

    @staticmethod
    def write(doc: Document) -> str:
        return to_markdown(doc)
