"""Command-line interface for ureca_document_parser.

Usage:
    ureca_document_parser document.hwp -o output.md
    ureca_document_parser document.hwpx -f markdown -o output.md
    ureca_document_parser --list-formats
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .registry import get_registry


def main() -> None:
    registry = get_registry()

    parser = argparse.ArgumentParser(
        prog="ureca_document_parser",
        description="문서 파일을 다양한 형식으로 변환합니다.",
    )
    parser.add_argument(
        "input_file",
        nargs="?",
        help="변환할 입력 파일 경로",
    )
    parser.add_argument(
        "--output",
        "-o",
        help="출력 파일 경로 (미지정 시 stdout 출력)",
    )
    parser.add_argument(
        "--format",
        "-f",
        default="markdown",
        help="출력 형식 (기본값: markdown)",
    )
    parser.add_argument(
        "--list-formats",
        action="store_true",
        help="지원하는 입력/출력 형식을 출력합니다",
    )

    args = parser.parse_args()

    if args.list_formats:
        print("지원 입력 형식:", ", ".join(registry.supported_extensions))
        print("지원 출력 형식:", ", ".join(registry.supported_formats))
        return

    if not args.input_file:
        parser.print_help()
        sys.exit(1)

    input_path = Path(args.input_file)
    if not input_path.exists():
        print(f"오류: 파일을 찾을 수 없습니다: {input_path}", file=sys.stderr)
        sys.exit(1)

    try:
        doc = registry.parse(input_path)
    except ValueError as e:
        print(f"오류: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        result = registry.write(doc, args.format)
    except ValueError as e:
        print(f"오류: {e}", file=sys.stderr)
        sys.exit(1)

    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(result, encoding="utf-8")
        print(f"변환 완료: {output_path}")
    else:
        print(result)
