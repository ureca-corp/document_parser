"""Tests for ureca_document_parser.hwpx.parser."""

from __future__ import annotations

import zipfile
from pathlib import Path

import pytest

from ureca_document_parser.hwpx.parser import (
    _detect_heading_level,
    _find_section_files,
    _strip_ns,
    parse_hwpx,
)
from ureca_document_parser.models import ParseError


class TestStripNs:
    def test_with_namespace(self):
        assert _strip_ns("{http://example.com}tag") == "tag"

    def test_without_namespace(self):
        assert _strip_ns("tag") == "tag"

    def test_multiple_braces(self):
        assert _strip_ns("{ns1}{ns2}tag") == "tag"


class TestFindSectionFiles:
    def test_finds_sections_by_pattern(self, tmp_path):
        zf_path = tmp_path / "test.hwpx"
        with zipfile.ZipFile(zf_path, "w") as zf:
            zf.writestr("Contents/section0.xml", "<root/>")
            zf.writestr("Contents/section1.xml", "<root/>")
            zf.writestr("other.txt", "")

        with zipfile.ZipFile(zf_path, "r") as zf:
            sections = _find_section_files(zf)
            assert len(sections) == 2
            assert all("section" in s.lower() for s in sections)


class TestParseHwpx:
    def test_parse_nonexistent_file(self):
        with pytest.raises(ParseError, match="파일을 찾을 수 없습니다"):
            parse_hwpx("/nonexistent/file.hwpx")

    def test_parse_invalid_file(self, tmp_path):
        bad_file = tmp_path / "bad.hwpx"
        bad_file.write_text("not a zip file")
        with pytest.raises(ParseError, match="유효한 HWPX 파일이 아닙니다"):
            parse_hwpx(bad_file)

    def test_parse_minimal_hwpx(self, tmp_path):
        """최소 구조의 HWPX ZIP을 생성하여 파싱 테스트."""
        section_xml = """<?xml version="1.0" encoding="UTF-8"?>
        <sec>
            <p>
                <run><t>테스트 텍스트</t></run>
            </p>
        </sec>"""

        zf_path = tmp_path / "test.hwpx"
        with zipfile.ZipFile(zf_path, "w") as zf:
            zf.writestr("Contents/section0.xml", section_xml)

        doc = parse_hwpx(zf_path)
        assert doc.metadata.source_format == "hwpx"
        assert len(doc.elements) > 0
        assert doc.elements[0].text == "테스트 텍스트"

    def test_extensions(self):
        from ureca_document_parser.hwpx import HwpxParser

        assert HwpxParser.extensions() == [".hwpx"]
