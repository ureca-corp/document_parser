"""Format registry — maps file extensions to parsers and format names to writers."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .models import Document


class FormatRegistry:
    """Central registry for parsers and writers.

    Parsers are registered by file extension (e.g. '.hwp').
    Writers are registered by format name (e.g. 'markdown').
    """

    def __init__(self) -> None:
        self._parsers: dict[str, Any] = {}   # ext -> Parser class
        self._writers: dict[str, Any] = {}   # format_name -> Writer class

    def register_parser(self, cls: Any) -> None:
        """Register a parser class. Must have extensions() and parse() methods."""
        for ext in cls.extensions():
            self._parsers[ext.lower()] = cls

    def register_writer(self, cls: Any) -> None:
        """Register a writer class. Must have format_name() and write() methods."""
        self._writers[cls.format_name().lower()] = cls

    def parse(self, filepath: Path | str) -> Document:
        """Parse a file using the appropriate parser based on extension."""
        path = Path(filepath)
        ext = path.suffix.lower()
        parser_cls = self._parsers.get(ext)
        if parser_cls is None:
            supported = ", ".join(sorted(self._parsers.keys()))
            raise ValueError(
                f"지원하지 않는 파일 형식입니다: {ext} (지원: {supported})"
            )
        return parser_cls.parse(path)

    def write(self, doc: Document, format_name: str) -> str:
        """Write a document using the specified output format."""
        writer_cls = self._writers.get(format_name.lower())
        if writer_cls is None:
            supported = ", ".join(sorted(self._writers.keys()))
            raise ValueError(
                f"지원하지 않는 출력 형식입니다: {format_name} (지원: {supported})"
            )
        return writer_cls.write(doc)

    @property
    def supported_extensions(self) -> list[str]:
        """List of supported input file extensions."""
        return sorted(self._parsers.keys())

    @property
    def supported_formats(self) -> list[str]:
        """List of supported output format names."""
        return sorted(self._writers.keys())


_registry: FormatRegistry | None = None


def get_registry() -> FormatRegistry:
    """Get the global format registry (singleton, lazily initialized)."""
    global _registry
    if _registry is None:
        _registry = FormatRegistry()
        _auto_register(_registry)
    return _registry


def _auto_register(registry: FormatRegistry) -> None:
    """Auto-discover and register all built-in parsers and writers."""
    # Parsers
    try:
        from .parsers.hwp import HwpParser
        registry.register_parser(HwpParser)
    except ImportError:
        pass

    try:
        from .parsers.hwpx import HwpxParser
        registry.register_parser(HwpxParser)
    except ImportError:
        pass

    # Writers
    try:
        from .writers.markdown import MarkdownWriter
        registry.register_writer(MarkdownWriter)
    except ImportError:
        pass
