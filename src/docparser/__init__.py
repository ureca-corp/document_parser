"""docparser — Multi-format document parser and converter.

Supports HWP, HWPX input formats and Markdown output.

Usage:
    # Low-level: direct parser/writer import
    from docparser.parsers.hwp import HwpParser
    from docparser.writers.markdown import MarkdownWriter
    doc = HwpParser.parse("document.hwp")
    md = MarkdownWriter.write(doc)

    # Mid-level: registry-based auto-routing
    from docparser import get_registry
    registry = get_registry()
    doc = registry.parse("document.hwp")
    md = registry.write(doc, "markdown")

    # High-level: one-line conversion
    from docparser import convert
    convert("document.hwp", "output.md")
"""

from __future__ import annotations

from pathlib import Path

from .models import (
    Document,
    DocumentElement,
    HorizontalRule,
    Image,
    Link,
    ListItem,
    Metadata,
    Paragraph,
    ParseError,
    Table,
    TableCell,
    TableRow,
)
from .protocols import Parser, Writer
from .registry import get_registry

__all__ = [
    # Models
    "Document",
    "DocumentElement",
    "HorizontalRule",
    "Image",
    "Link",
    "ListItem",
    "Metadata",
    "Paragraph",
    "ParseError",
    "Table",
    "TableCell",
    "TableRow",
    # Protocols
    "Parser",
    "Writer",
    # Registry
    "get_registry",
    # Convenience
    "convert",
]


def convert(
    input_path: str | Path,
    output_path: str | Path,
    *,
    format: str = "markdown",
) -> None:
    """입력 파일을 파싱하여 지정 포맷으로 변환, 파일에 저장한다.

    Args:
        input_path: 변환할 입력 파일 경로
        output_path: 출력 파일 경로
        format: 출력 포맷 이름 (기본값: "markdown")
    """
    registry = get_registry()
    doc = registry.parse(input_path)
    result = registry.write(doc, format)

    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(result, encoding="utf-8")
