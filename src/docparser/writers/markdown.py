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
)


def to_markdown(doc: Document) -> str:
    """Document를 Markdown 문자열로 변환한다."""
    parts: list[str] = []

    for element in doc.elements:
        if isinstance(element, Paragraph):
            parts.append(_render_paragraph(element))
        elif isinstance(element, Table):
            rendered = _render_table(element)
            if rendered:
                parts.append(rendered)
        elif isinstance(element, Image):
            parts.append(_render_image(element))
        elif isinstance(element, ListItem):
            parts.append(_render_list_item(element))
        elif isinstance(element, Link):
            parts.append(_render_link(element))
        elif isinstance(element, HorizontalRule):
            parts.append("---")

    return "\n\n".join(parts) + "\n"


def _render_paragraph(para: Paragraph) -> str:
    """Paragraph를 Markdown으로 렌더링한다."""
    text = para.text
    if para.heading_level > 0:
        prefix = "#" * para.heading_level
        return f"{prefix} {text}"
    return text


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
                cell = row.cells[i]
                cell_text = "<br>".join(p.text for p in cell.paragraphs if p.text)
                cell_text = cell_text.replace("\n", "<br>")
                cell_text = cell_text.replace("|", "\\|")
                row_texts.append(cell_text)
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
    lines.append(
        "| " + " | ".join("-" * col_widths[i] for i in range(n_cols)) + " |"
    )

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


def _render_list_item(item: ListItem) -> str:
    """ListItem을 Markdown으로 렌더링한다."""
    indent = "  " * item.level
    marker = f"{item.level + 1}." if item.ordered else "-"
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
