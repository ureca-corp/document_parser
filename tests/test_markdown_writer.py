"""Tests for ureca_document_parser.writers.markdown."""

from __future__ import annotations

from ureca_document_parser.models import (
    Document,
    HorizontalRule,
    Image,
    Link,
    ListItem,
    Metadata,
    Paragraph,
    Table,
    TableCell,
    TableRow,
)
from ureca_document_parser.writers.markdown import to_markdown


class TestRenderParagraph:
    def test_normal_text(self):
        doc = Document(elements=[Paragraph(text="hello")])
        assert to_markdown(doc).strip() == "hello"

    def test_heading_levels(self):
        for level in range(1, 7):
            doc = Document(elements=[Paragraph(text="title", heading_level=level)])
            expected = "#" * level + " title"
            assert to_markdown(doc).strip() == expected


class TestRenderTable:
    def test_simple_table(self, doc_with_table):
        md = to_markdown(doc_with_table)
        assert "| 이름" in md
        assert "| 홍길동" in md
        assert "---" in md

    def test_empty_table_skipped(self):
        doc = Document(elements=[Table(rows=[])])
        assert to_markdown(doc).strip() == ""

    def test_cell_pipe_escaped(self):
        doc = Document(elements=[
            Table(rows=[
                TableRow(cells=[
                    TableCell(content=[Paragraph(text="a|b")]),
                ]),
            ]),
        ])
        md = to_markdown(doc)
        assert "a\\|b" in md


class TestRenderListItem:
    def test_unordered_list(self):
        doc = Document(elements=[
            ListItem(text="항목 1", ordered=False),
            ListItem(text="항목 2", ordered=False),
        ])
        md = to_markdown(doc)
        lines = md.strip().split("\n")
        assert lines[0] == "- 항목 1"
        assert lines[1] == "- 항목 2"

    def test_ordered_list(self):
        doc = Document(elements=[
            ListItem(text="첫째", ordered=True),
            ListItem(text="둘째", ordered=True),
            ListItem(text="셋째", ordered=True),
        ])
        md = to_markdown(doc)
        lines = md.strip().split("\n")
        assert lines[0] == "1. 첫째"
        assert lines[1] == "2. 둘째"
        assert lines[2] == "3. 셋째"

    def test_nested_list(self):
        doc = Document(elements=[
            ListItem(text="상위", level=0, ordered=False),
            ListItem(text="하위", level=1, ordered=False),
        ])
        md = to_markdown(doc)
        assert "  - 하위" in md

    def test_list_items_grouped(self):
        """연속 ListItem이 \\n\\n이 아닌 \\n으로 연결되는지 확인."""
        doc = Document(elements=[
            ListItem(text="a", ordered=False),
            ListItem(text="b", ordered=False),
        ])
        md = to_markdown(doc)
        # 두 항목 사이에 빈 줄이 없어야 함
        assert "- a\n- b" in md


class TestRenderImage:
    def test_image_with_source(self):
        doc = Document(elements=[Image(alt_text="photo", source="pic.png")])
        assert to_markdown(doc).strip() == "![photo](pic.png)"

    def test_image_without_source(self):
        doc = Document(elements=[Image(alt_text="photo")])
        assert to_markdown(doc).strip() == "![photo]()"

    def test_image_default_alt(self):
        doc = Document(elements=[Image(source="x.png")])
        assert "![image]" in to_markdown(doc)


class TestRenderLink:
    def test_link(self):
        doc = Document(elements=[Link(text="click", url="https://example.com")])
        assert to_markdown(doc).strip() == "[click](https://example.com)"


class TestRenderHorizontalRule:
    def test_hr(self):
        doc = Document(elements=[HorizontalRule()])
        assert to_markdown(doc).strip() == "---"


class TestFullDocument:
    def test_all_elements(self, doc_with_all_elements):
        md = to_markdown(doc_with_all_elements)
        assert "# 문서 제목" in md
        assert "일반 텍스트" in md
        assert "| A" in md
        assert "- 항목 1" in md
        assert "![사진](img.png)" in md
        assert "[링크](https://example.com)" in md
        assert "---" in md
