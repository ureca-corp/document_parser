"""Tests for ureca_document_parser.registry."""

from __future__ import annotations

import pytest

from ureca_document_parser.models import Document, Metadata, Paragraph
from ureca_document_parser.registry import FormatRegistry, get_registry


class TestFormatRegistry:
    def test_register_and_parse(self, tmp_path):
        """파서 등록 후 parse 호출이 올바른 파서로 라우팅되는지 확인."""
        registry = FormatRegistry()

        class FakeParser:
            @staticmethod
            def extensions() -> list[str]:
                return [".fake"]

            @staticmethod
            def parse(filepath) -> Document:
                return Document(
                    elements=[Paragraph(text="fake")],
                    metadata=Metadata(source_format="fake"),
                )

        registry.register_parser(FakeParser)
        fake_file = tmp_path / "test.fake"
        fake_file.write_text("content")
        doc = registry.parse(fake_file)
        assert doc.metadata.source_format == "fake"
        assert len(doc.elements) == 1

    def test_register_writer(self):
        registry = FormatRegistry()

        class FakeWriter:
            @staticmethod
            def format_name() -> str:
                return "fake"

            @staticmethod
            def file_extension() -> str:
                return ".fk"

            @staticmethod
            def write(doc: Document) -> str:
                return "fake output"

        registry.register_writer(FakeWriter)
        doc = Document()
        assert registry.write(doc, "fake") == "fake output"

    def test_unsupported_extension_raises(self):
        registry = FormatRegistry()
        with pytest.raises(ValueError, match="지원하지 않는 파일 형식"):
            registry.parse("test.xyz")

    def test_unsupported_format_raises(self):
        registry = FormatRegistry()
        with pytest.raises(ValueError, match="지원하지 않는 출력 형식"):
            registry.write(Document(), "nonexistent")

    def test_supported_extensions(self):
        registry = FormatRegistry()

        class FakeParser:
            @staticmethod
            def extensions():
                return [".a", ".b"]

            @staticmethod
            def parse(filepath):
                return Document()

        registry.register_parser(FakeParser)
        assert registry.supported_extensions == [".a", ".b"]

    def test_supported_formats(self):
        registry = FormatRegistry()

        class FakeWriter:
            @staticmethod
            def format_name():
                return "html"

            @staticmethod
            def file_extension():
                return ".html"

            @staticmethod
            def write(doc):
                return ""

        registry.register_writer(FakeWriter)
        assert registry.supported_formats == ["html"]


class TestGetRegistry:
    def test_singleton_returns_same_instance(self):
        r1 = get_registry()
        r2 = get_registry()
        assert r1 is r2

    def test_has_builtin_parsers(self):
        registry = get_registry()
        assert ".hwp" in registry.supported_extensions
        assert ".hwpx" in registry.supported_extensions

    def test_has_builtin_writers(self):
        registry = get_registry()
        assert "markdown" in registry.supported_formats
