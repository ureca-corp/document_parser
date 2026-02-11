"""Parser and Writer protocols — structural subtyping interfaces.

Implement these protocols to add new input formats or output formats.
No inheritance required; just match the method signatures.
"""

from __future__ import annotations

from pathlib import Path
from typing import Protocol

from .models import Document


class Parser(Protocol):
    """Protocol for document parsers (e.g. HWP, HWPX, PDF)."""

    @staticmethod
    def extensions() -> list[str]:
        """Supported file extensions, e.g. ['.hwp']."""
        ...

    @staticmethod
    def parse(filepath: Path | str) -> Document:
        """Parse a file and return a Document."""
        ...


class Writer(Protocol):
    """Protocol for document writers (e.g. Markdown, HTML)."""

    @staticmethod
    def format_name() -> str:
        """Output format name, e.g. 'markdown'."""
        ...

    @staticmethod
    def file_extension() -> str:
        """Output file extension, e.g. '.md'."""
        ...

    @staticmethod
    def write(doc: Document) -> str:
        """Convert a Document to the output format string."""
        ...
