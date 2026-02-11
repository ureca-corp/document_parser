"""Tests for ureca_document_parser.cli."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

SAMPLE_HWP = Path(__file__).parents[1] / "document.hwp"


def _run_cli(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-m", "ureca_document_parser", *args],
        capture_output=True,
        text=True,
    )


class TestCli:
    def test_no_args_prints_help(self):
        result = _run_cli()
        assert result.returncode == 1

    def test_list_formats(self):
        result = _run_cli("--list-formats")
        assert result.returncode == 0
        assert ".hwp" in result.stdout
        assert "markdown" in result.stdout

    def test_nonexistent_file(self):
        result = _run_cli("/nonexistent/file.hwp")
        assert result.returncode == 1
        assert "오류" in result.stderr or "찾을 수 없습니다" in result.stderr

    @pytest.mark.skipif(not SAMPLE_HWP.exists(), reason="sample HWP file not available")
    def test_convert_to_stdout(self):
        result = _run_cli(str(SAMPLE_HWP))
        assert result.returncode == 0
        assert len(result.stdout) > 0

    @pytest.mark.skipif(not SAMPLE_HWP.exists(), reason="sample HWP file not available")
    def test_convert_to_file(self, tmp_path):
        output = tmp_path / "output.md"
        result = _run_cli(str(SAMPLE_HWP), "-o", str(output))
        assert result.returncode == 0
        assert output.exists()
        assert output.read_text(encoding="utf-8").strip() != ""
