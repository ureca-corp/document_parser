# 포맷 확장 가이드

새 입력 포맷(Parser)이나 출력 포맷(Writer)을 추가하는 방법을 안내해요.

## 새 Parser 추가

### 1. 파서 패키지 생성

`src/ureca_document_parser/` 아래에 확장자명 디렉토리를 만들고 `parser.py`를 생성하세요.

```python
# src/ureca_document_parser/pdf/parser.py
"""PDF format parser."""

from __future__ import annotations

from pathlib import Path

from ..models import Document, Metadata, Paragraph


def parse_pdf(filepath: str | Path) -> Document:
    """PDF 파일을 파싱하여 Document를 반환한다."""
    import pymupdf  # lazy import (optional dependency)

    doc = Document(metadata=Metadata(source_format="pdf"))
    pdf = pymupdf.open(str(filepath))

    for page in pdf:
        text = page.get_text().strip()
        if text:
            doc.elements.append(Paragraph(text=text))

    return doc


class PdfParser:
    """PDF parser — Parser protocol implementation."""

    @staticmethod
    def extensions() -> list[str]:
        return [".pdf"]

    @staticmethod
    def parse(filepath: Path | str) -> Document:
        return parse_pdf(filepath)
```

`__init__.py`에서 re-export해 주세요.

```python
# src/ureca_document_parser/pdf/__init__.py
from .parser import PdfParser

__all__ = ["PdfParser"]
```

핵심 규칙은 다음과 같아요.

- `protocols.py`의 `Parser` Protocol 시그니처를 따라야 해요
- `models.py`의 `Document`를 반환해야 해요
- 선택적 의존성은 **함수 내부에서 lazy import**해야 해요

### 2. 레지스트리에 등록

`src/ureca_document_parser/registry.py`의 `_auto_register()` 함수에 추가하세요.

```python
def _auto_register(registry: FormatRegistry) -> None:
    # ... 기존 파서들 ...

    try:
        from .pdf import PdfParser
        registry.register_parser(PdfParser)
    except ImportError:
        pass  # pymupdf 미설치 시 건너뜀
```

### 3. pyproject.toml에 optional dependency 추가 (선택)

```toml
[project.optional-dependencies]
pdf = ["pymupdf>=1.24"]
all = ["ureca_document_parser[pdf,ocr]"]  # all에도 추가
```

### 완료

이제 다음이 자동으로 동작해요.

```python
from ureca_document_parser import get_registry
doc = get_registry().parse("document.pdf")
```

```bash
# CLI
ureca_document_parser document.pdf -o output.md
```

---

## 새 Writer 추가

### 1. Writer 모듈 생성

`src/ureca_document_parser/writers/` 아래에 새 파일을 만드세요.

```python
# src/ureca_document_parser/writers/html.py
"""HTML writer."""

from __future__ import annotations

from ..models import Document, Paragraph, Table


def to_html(doc: Document) -> str:
    """Document를 HTML 문자열로 변환한다."""
    parts = ["<html><body>"]

    for element in doc.elements:
        if isinstance(element, Paragraph):
            if element.heading_level > 0:
                tag = f"h{element.heading_level}"
                parts.append(f"<{tag}>{element.text}</{tag}>")
            else:
                parts.append(f"<p>{element.text}</p>")
        elif isinstance(element, Table):
            parts.append(_render_table(element))

    parts.append("</body></html>")
    return "\n".join(parts)


def _render_table(table: Table) -> str:
    # ... 테이블 HTML 렌더링 ...
    pass


class HtmlWriter:
    """HTML writer — Writer protocol implementation."""

    @staticmethod
    def format_name() -> str:
        return "html"

    @staticmethod
    def file_extension() -> str:
        return ".html"

    @staticmethod
    def write(doc: Document) -> str:
        return to_html(doc)
```

### 2. 레지스트리에 등록

```python
# registry.py의 _auto_register()
try:
    from .writers.html import HtmlWriter
    registry.register_writer(HtmlWriter)
except ImportError:
    pass
```

### 완료

이제 다음이 자동으로 동작해요.

```python
from ureca_document_parser import get_registry
md = get_registry().write(doc, "html")
```

```bash
# CLI
ureca_document_parser document.hwp -f html -o output.html
```

---

## 체크리스트

새 포맷을 추가할 때 다음 사항을 확인하세요.

- [ ] Protocol 시그니처와 호환되는 클래스를 작성했나요?
- [ ] `models.py`의 `Document`만 사용해서 입출력하나요?
- [ ] `registry.py`의 `_auto_register()`에 `try/except ImportError`로 등록했나요?
- [ ] 선택적 의존성을 `pyproject.toml`의 `[project.optional-dependencies]`에 추가했나요?
- [ ] lazy import를 사용하고 있나요? (함수 내부에서 import)
