"""ureca_document_parser — Multi-format document parser and converter.

Supports HWP, HWPX input formats and Markdown output.

Usage:
    # Save as file
    from ureca_document_parser import convert
    convert("document.hwp", "output.md")

    # Return as string
    markdown = convert("document.hwp")

    # Convert to LangChain chunks for RAG (requires langchain extra)
    chunks = convert("document.hwp", chunks=True, chunk_size=1000, chunk_overlap=200)
"""

from __future__ import annotations

from importlib.metadata import version
from pathlib import Path
from typing import TYPE_CHECKING

from .models import ParseError
from .registry import get_registry

if TYPE_CHECKING:
    from langchain_core.documents import Document as LCDocument

__version__ = version("ureca_document_parser")

__all__ = [
    # Main API
    "convert",

    # Exceptions
    "ParseError",
]


def convert(
    input_path: str | Path,
    output_path: str | Path | None = None,
    *,
    format: str = "markdown",
    chunks: bool = False,
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
) -> str | list[LCDocument] | None:
    """파일을 변환합니다.

    Args:
        input_path: 변환할 입력 파일 경로
        output_path: 출력 파일 경로 (None이면 반환만, chunks=True면 무시됨)
        format: 출력 포맷 이름 (기본값: "markdown")
        chunks: True면 LangChain Document 청크로 반환 (requires langchain extra)
        chunk_size: 청크 크기 (chunks=True일 때만 사용, 기본값: 1000)
        chunk_overlap: 청크 오버랩 (chunks=True일 때만 사용, 기본값: 200)

    Returns:
        - chunks=True: LangChain Document 리스트
        - chunks=False, output_path=None: 변환된 문자열
        - chunks=False, output_path 지정: None (파일에 저장됨)

    Examples:
        >>> # 파일에 저장
        >>> convert("report.hwp", "report.md")

        >>> # 문자열로 반환
        >>> markdown = convert("report.hwp")

        >>> # LangChain 청크로 반환
        >>> chunks = convert("report.hwp", chunks=True)

        >>> # 청크 크기 커스텀
        >>> chunks = convert(
        ...     "report.hwp", chunks=True, chunk_size=500, chunk_overlap=100
        ... )
    """
    registry = get_registry()
    doc = registry.parse(input_path)

    if chunks:
        # LangChain 청크로 반환
        try:
            from langchain_text_splitters import RecursiveCharacterTextSplitter
        except ImportError:
            raise ImportError(
                "chunks=True requires the langchain extra. "
                "Install it with: pip install ureca_document_parser[langchain]"
            ) from None

        md = registry.write(doc, format)
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )
        return splitter.create_documents(
            [md],
            metadatas=[
                {
                    "source": str(input_path),
                    "format": doc.metadata.source_format,
                }
            ],
        )
    else:
        # Markdown 문자열
        result = registry.write(doc, format)

        if output_path:
            # 파일에 저장
            out = Path(output_path)
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(result, encoding="utf-8")
            return None
        else:
            # 문자열 반환
            return result
