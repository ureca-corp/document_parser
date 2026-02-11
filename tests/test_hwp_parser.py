"""Tests for ureca_document_parser.hwp.parser."""

from __future__ import annotations

import struct
from pathlib import Path

import pytest

from ureca_document_parser.hwp import (
    CharInfo,
    Record,
    RecordCursor,
    extract_text,
    has_table_marker,
    read_bstr,
    scan_para_chars,
)
from ureca_document_parser.models import ParseError

SAMPLE_HWP = Path(__file__).parents[1] / "document.hwp"


class TestReadBstr:
    def test_simple_string(self):
        text = "ABC"
        encoded = text.encode("utf-16-le")
        data = struct.pack("<H", len(text)) + encoded
        result, offset = read_bstr(data, 0)
        assert result == "ABC"
        assert offset == 2 + len(encoded)

    def test_empty_string(self):
        data = struct.pack("<H", 0)
        result, offset = read_bstr(data, 0)
        assert result == ""
        assert offset == 2

    def test_truncated_data(self):
        result, _ = read_bstr(b"\x01", 0)
        assert result == ""


class TestScanParaChars:
    def test_printable_chars(self):
        data = "AB".encode("utf-16-le")
        chars = list(scan_para_chars(data))
        assert len(chars) == 2
        assert chars[0].code == ord("A")
        assert chars[1].code == ord("B")

    def test_extended_ctrl_char(self):
        # code 2 = 확장 제어문자 (16바이트)
        data = struct.pack("<H", 2) + b"\x00" * 14 + "A".encode("utf-16-le")
        chars = list(scan_para_chars(data))
        assert chars[0].code == 2
        assert chars[0].size == 16
        assert chars[1].code == ord("A")


class TestExtractText:
    def test_basic_text(self):
        data = "Hello".encode("utf-16-le")
        assert extract_text(data) == "Hello"

    def test_tab_converted(self):
        data = struct.pack("<H", 9) + b"\x00" * 14 + " ".encode("utf-16-le")
        text = extract_text(data)
        assert "\t" in text

    def test_line_break(self):
        data = struct.pack("<H", 10) + "A".encode("utf-16-le")
        text = extract_text(data)
        assert "\n" in text


class TestHasTableMarker:
    def test_with_marker(self):
        # code 11 = table/GSO marker (확장 제어문자)
        data = struct.pack("<H", 11) + b"\x00" * 14
        assert has_table_marker(data) is True

    def test_without_marker(self):
        data = "hello".encode("utf-16-le")
        assert has_table_marker(data) is False


class TestRecordCursor:
    def test_basic_traversal(self):
        records = [Record(tag=1, level=0, data=b""), Record(tag=2, level=0, data=b"")]
        cursor = RecordCursor(records)
        assert cursor.has_next()
        r = cursor.advance()
        assert r.tag == 1
        r = cursor.advance()
        assert r.tag == 2
        assert not cursor.has_next()

    def test_peek(self):
        records = [Record(tag=5, level=0, data=b"")]
        cursor = RecordCursor(records)
        assert cursor.peek().tag == 5
        assert cursor.pos == 0  # peek doesn't advance


class TestParseHwp:
    @pytest.mark.skipif(not SAMPLE_HWP.exists(), reason="sample HWP file not available")
    def test_parse_sample(self):
        from ureca_document_parser.hwp import HwpParser

        doc = HwpParser.parse(SAMPLE_HWP)
        assert doc.metadata.source_format == "hwp"
        assert len(doc.elements) > 0

    def test_parse_nonexistent_file(self):
        from ureca_document_parser.hwp import HwpParser

        with pytest.raises(ParseError, match="파일을 찾을 수 없습니다"):
            HwpParser.parse("/nonexistent/file.hwp")

    def test_parse_invalid_file(self, tmp_path):
        from ureca_document_parser.hwp import HwpParser

        bad_file = tmp_path / "bad.hwp"
        bad_file.write_text("not an OLE file")
        with pytest.raises(ParseError, match="유효한 HWP 파일이 아닙니다"):
            HwpParser.parse(bad_file)

    def test_extensions(self):
        from ureca_document_parser.hwp import HwpParser

        assert HwpParser.extensions() == [".hwp"]
