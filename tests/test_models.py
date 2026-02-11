"""Tests for ureca_document_parser.models."""

from ureca_document_parser.models import (
    Document,
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


class TestDocument:
    def test_default_empty(self):
        doc = Document()
        assert doc.elements == []
        assert doc.metadata.title == ""
        assert doc.metadata.source_format == ""

    def test_with_elements(self, simple_doc):
        assert len(simple_doc.elements) == 4
        assert simple_doc.metadata.source_format == "test"


class TestParagraph:
    def test_normal_paragraph(self):
        p = Paragraph(text="hello")
        assert p.text == "hello"
        assert p.heading_level == 0

    def test_heading(self):
        p = Paragraph(text="title", heading_level=1)
        assert p.heading_level == 1


class TestTable:
    def test_empty_table(self):
        t = Table()
        assert t.rows == []

    def test_table_structure(self):
        cell = TableCell(content=[Paragraph(text="data")])
        row = TableRow(cells=[cell])
        table = Table(rows=[row])
        assert len(table.rows) == 1
        assert len(table.rows[0].cells) == 1
        assert table.rows[0].cells[0].content[0].text == "data"


class TestParseError:
    def test_is_exception(self):
        err = ParseError("bad file")
        assert isinstance(err, Exception)
        assert str(err) == "bad file"


class TestMetadata:
    def test_extra_dict(self):
        m = Metadata(title="T", extra={"key": "val"})
        assert m.extra["key"] == "val"
