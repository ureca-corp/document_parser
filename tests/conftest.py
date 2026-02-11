"""Shared fixtures for ureca_document_parser tests."""

from __future__ import annotations

from pathlib import Path

import pytest

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
from ureca_document_parser.registry import _reset_registry

FIXTURES_DIR = Path(__file__).parent / "fixtures"
SAMPLE_HWP = Path(__file__).parents[1] / "document.hwp"


@pytest.fixture(autouse=True)
def _clean_registry():
    """각 테스트 전후로 글로벌 레지스트리를 리셋한다."""
    _reset_registry()
    yield
    _reset_registry()


@pytest.fixture()
def simple_doc() -> Document:
    """테스트용 간단한 Document."""
    return Document(
        elements=[
            Paragraph(text="제목", heading_level=1),
            Paragraph(text="본문 텍스트입니다."),
            Paragraph(text="소제목", heading_level=2),
            Paragraph(text="두 번째 문단."),
        ],
        metadata=Metadata(source_format="test"),
    )


@pytest.fixture()
def doc_with_table() -> Document:
    """테이블이 포함된 Document."""
    return Document(
        elements=[
            Paragraph(text="표 제목", heading_level=2),
            Table(rows=[
                TableRow(cells=[
                    TableCell(content=[Paragraph(text="이름")]),
                    TableCell(content=[Paragraph(text="나이")]),
                ]),
                TableRow(cells=[
                    TableCell(content=[Paragraph(text="홍길동")]),
                    TableCell(content=[Paragraph(text="30")]),
                ]),
            ]),
        ],
        metadata=Metadata(source_format="test"),
    )


@pytest.fixture()
def doc_with_all_elements() -> Document:
    """모든 요소 타입이 포함된 Document."""
    return Document(
        elements=[
            Paragraph(text="문서 제목", heading_level=1),
            Paragraph(text="일반 텍스트"),
            Table(rows=[
                TableRow(cells=[
                    TableCell(content=[Paragraph(text="A")]),
                    TableCell(content=[Paragraph(text="B")]),
                ]),
            ]),
            ListItem(text="항목 1", level=0, ordered=False),
            ListItem(text="항목 2", level=0, ordered=False),
            ListItem(text="하위 항목", level=1, ordered=False),
            Image(alt_text="사진", source="img.png"),
            Link(text="링크", url="https://example.com"),
            HorizontalRule(),
        ],
        metadata=Metadata(source_format="test"),
    )
