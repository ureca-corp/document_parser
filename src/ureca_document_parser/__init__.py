"""ureca_document_parser — Multi-format document parser and converter.

Supports HWP, HWPX input formats and Markdown output.

Usage:
    # Low-level: direct parser/writer import
    from ureca_document_parser.hwp import HwpParser
    from ureca_document_parser.writers.markdown import MarkdownWriter
    doc = HwpParser.parse("document.hwp")
    md = MarkdownWriter.write(doc)

    # Mid-level: registry-based auto-routing
    from ureca_document_parser import get_registry
    registry = get_registry()
    doc = registry.parse("document.hwp")
    md = registry.write(doc, "markdown")

    # High-level: one-line conversion
    from ureca_document_parser import convert
    convert("document.hwp", "output.md")

    # High-level: chunked output for RAG pipelines (requires langchain extra)
    from ureca_document_parser import convert_to_chunks
    chunks = convert_to_chunks("document.hwp", chunk_size=1000, chunk_overlap=200)
"""

from __future__ import annotations

from importlib.metadata import version
from pathlib import Path
from typing import TYPE_CHECKING

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

if TYPE_CHECKING:
    from langchain_core.documents import Document as LCDocument

__version__ = version("ureca_document_parser")

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
    "convert_to_chunks",
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


def convert_to_chunks(
    input_path: str | Path,
    *,
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
) -> list[LCDocument]:
    """파일을 파싱하고 TextSplitter로 분할하여 LangChain Document를 반환.

    Requires the ``langchain`` extra: ``pip install ureca_document_parser[langchain]``

    Args:
        input_path: 변환할 입력 파일 경로
        chunk_size: 청크 크기 (기본값: 1000)
        chunk_overlap: 청크 오버랩 (기본값: 200)

    Returns:
        분할된 LangChain Document 리스트
    """
    try:
        from langchain_text_splitters import RecursiveCharacterTextSplitter
    except ImportError:
        raise ImportError(
            "convert_to_chunks requires the langchain extra. "
            "Install it with: pip install ureca_document_parser[langchain]"
        ) from None

    registry = get_registry()
    doc = registry.parse(input_path)
    md = registry.write(doc, "markdown")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )
    return splitter.create_documents(
        [md],
        metadatas=[{"source": str(input_path), "format": doc.metadata.source_format}],
    )
