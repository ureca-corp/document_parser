"""Document model — intermediate representation for all parsers.

All parsers produce a Document containing a list of DocumentElement instances.
Writers consume this model to generate output in various formats.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Paragraph:
    text: str
    heading_level: int = 0  # 0 = normal, 1-6 = heading


@dataclass
class TableCell:
    content: list[Paragraph | Table] = field(default_factory=list)


@dataclass
class TableRow:
    cells: list[TableCell] = field(default_factory=list)


@dataclass
class Table:
    rows: list[TableRow] = field(default_factory=list)


@dataclass
class Image:
    alt_text: str = ""
    source: str = ""
    data: bytes = b""
    ocr_text: str = ""


@dataclass
class ListItem:
    text: str = ""
    level: int = 0
    ordered: bool = False


@dataclass
class Link:
    text: str = ""
    url: str = ""


@dataclass
class HorizontalRule:
    pass


@dataclass
class Metadata:
    title: str = ""
    author: str = ""
    source_format: str = ""
    extra: dict[str, str] = field(default_factory=dict)


type DocumentElement = Paragraph | Table | Image | ListItem | Link | HorizontalRule


class ParseError(Exception):
    """Raised when a document cannot be parsed."""


@dataclass
class Document:
    elements: list[DocumentElement] = field(default_factory=list)
    metadata: Metadata = field(default_factory=Metadata)
