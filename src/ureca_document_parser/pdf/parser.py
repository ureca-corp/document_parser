"""PDF parser implementation using pymupdf (fitz)."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from ..models import Document, Metadata, Paragraph, ParseError

if TYPE_CHECKING:
    from os import PathLike


class PdfParser:
    """Parser for PDF files using pymupdf.

    Extracts text content from PDF files and converts to Document model.
    """

    @staticmethod
    def extensions() -> list[str]:
        """Return list of supported file extensions."""
        return [".pdf"]

    @staticmethod
    def parse(file_path: str | PathLike[str]) -> Document:
        """Parse PDF file and return Document.

        Args:
            file_path: Path to PDF file

        Returns:
            Document with extracted content

        Raises:
            ParseError: If file cannot be parsed
        """
        try:
            import fitz  # pymupdf
        except ImportError:
            raise ParseError(
                "PDF support requires pymupdf. "
                "Install with: pip install ureca_document_parser[pdf]"
            ) from None

        path = Path(file_path)

        try:
            # Open PDF
            doc = fitz.open(path)

            # Extract metadata
            metadata = Metadata(
                title=doc.metadata.get("title") or path.stem,
                author=doc.metadata.get("author") or "",
                source_format="pdf",
                extra={
                    "pages": doc.page_count,
                    "producer": doc.metadata.get("producer", ""),
                    "creator": doc.metadata.get("creator", ""),
                },
            )

            # Extract text from each page
            elements = []
            for page in doc:
                text = page.get_text()

                # Split by paragraphs (double newline)
                paragraphs = text.split("\n\n")

                for para_text in paragraphs:
                    # Clean up whitespace
                    cleaned = " ".join(para_text.split())

                    if cleaned:  # Skip empty paragraphs
                        elements.append(
                            Paragraph(
                                text=cleaned,
                                heading_level=0,
                            )
                        )

            doc.close()

            return Document(elements=elements, metadata=metadata)

        except Exception as e:
            raise ParseError(f"Failed to parse PDF: {e}") from e
