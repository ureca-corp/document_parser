# 포맷 확장 가이드

!!! info "대상 독자"
    이 문서는 라이브러리에 직접 기여하여 새 포맷을 추가하려는 개발자를 위한 가이드예요.

## 새 Parser 추가하기

새 입력 포맷을 지원하려면 세 단계가 필요해요.

### 1. 파서 클래스 작성

`src/ureca_document_parser/` 아래에 새 디렉토리를 만들고 파서를 구현하세요. `Parser` Protocol의 두 메서드만 맞추면 돼요.

- `extensions()` — 지원하는 파일 확장자 리스트를 반환
- `parse(filepath)` — 파일을 파싱해서 `Document`를 반환

```python
from ureca_document_parser.models import Document, Metadata, Paragraph

class PdfParser:
    @staticmethod
    def extensions() -> list[str]:
        return [".pdf"]

    @staticmethod
    def parse(filepath):
        import pymupdf  # 선택적 의존성은 함수 안에서 import

        doc = Document(metadata=Metadata(source_format="pdf"))
        pdf = pymupdf.open(str(filepath))

        for page in pdf:
            text = page.get_text().strip()
            if text:
                doc.elements.append(Paragraph(text=text))

        return doc
```

**핵심 규칙**:

- 반드시 `Document`를 반환해야 해요
- 선택적 의존성은 **함수 내부에서 lazy import**해야 해요
- 상속은 필요 없어요 — 메서드 시그니처만 맞으면 Protocol과 호환돼요

### 2. 레지스트리에 등록

`registry.py`의 `_auto_register()` 함수에 추가하세요. `try/except ImportError`로 감싸서 의존성이 없을 때도 안전하게 동작하도록 해요.

```python
def _auto_register(registry: FormatRegistry) -> None:
    # ... 기존 파서들 ...

    try:
        from .pdf import PdfParser
        registry.register_parser(PdfParser)
    except ImportError:
        pass
```

### 3. optional dependency 추가 (선택)

외부 라이브러리가 필요하다면 `pyproject.toml`에 추가하세요.

```toml
[project.optional-dependencies]
pdf = ["pymupdf>=1.24"]
```

### 확인

등록이 완료되면 CLI와 Python API에서 자동으로 사용할 수 있어요.

```bash
uv run ureca_document_parser document.pdf -o output.md
```

```python
from ureca_document_parser import convert

convert("document.pdf", "output.md")
```

---

## 새 Writer 추가하기

새 출력 포맷을 지원하려는 경우에도 비슷한 흐름이에요. `Writer` Protocol의 세 메서드를 구현하면 돼요.

- `format_name()` — 포맷 이름을 반환 (예: `"html"`)
- `file_extension()` — 파일 확장자를 반환 (예: `".html"`)
- `write(doc)` — `Document`를 받아 출력 문자열을 반환

```python
from ureca_document_parser.models import Document, Paragraph

class HtmlWriter:
    @staticmethod
    def format_name() -> str:
        return "html"

    @staticmethod
    def file_extension() -> str:
        return ".html"

    @staticmethod
    def write(doc: Document) -> str:
        parts = []
        for element in doc.elements:
            if isinstance(element, Paragraph):
                if element.heading_level > 0:
                    tag = f"h{element.heading_level}"
                    parts.append(f"<{tag}>{element.text}</{tag}>")
                else:
                    parts.append(f"<p>{element.text}</p>")
        return "\n".join(parts)
```

레지스트리 등록 방법은 Parser와 동일해요.

```python
# registry.py의 _auto_register()
from .writers.html import HtmlWriter
registry.register_writer(HtmlWriter)
```

등록 후 CLI에서 `-f` 옵션으로 사용할 수 있어요.

```bash
uv run ureca_document_parser 보고서.hwp -f html -o 보고서.html
```

---

## 체크리스트

새 포맷을 추가할 때 다음 사항을 확인하세요.

- [ ] Protocol 시그니처와 호환되는 클래스를 작성했나요?
- [ ] `Document` 모델만 사용해서 입출력하나요?
- [ ] `_auto_register()`에 `try/except ImportError`로 등록했나요?
- [ ] 선택적 의존성을 `pyproject.toml`에 추가했나요?
- [ ] lazy import를 사용하고 있나요?
- [ ] 테스트 케이스를 작성했나요? (`tests/` 디렉토리)
- [ ] docstring을 작성했나요? (Google 스타일)

## 테스트 작성

새 파서나 Writer를 추가하면 반드시 테스트를 작성하세요.

### 파서 테스트 예시

```python
# tests/test_pdf_parser.py
from pathlib import Path
from ureca_document_parser.pdf import PdfParser
from ureca_document_parser import Paragraph

def test_pdf_parser():
    parser = PdfParser()
    doc = parser.parse("tests/fixtures/sample.pdf")

    assert doc.metadata.source_format == "pdf"
    assert len(doc.elements) > 0
    assert isinstance(doc.elements[0], Paragraph)
```

### Writer 테스트 예시

```python
# tests/test_html_writer.py
from ureca_document_parser import Document, Paragraph
from ureca_document_parser.writers.html import HtmlWriter

def test_html_writer():
    doc = Document(elements=[
        Paragraph(text="제목", heading_level=1),
        Paragraph(text="본문"),
    ])

    writer = HtmlWriter()
    html = writer.write(doc)

    assert "<h1>제목</h1>" in html
    assert "<p>본문</p>" in html
```

## 문서 업데이트

새 포맷을 추가하면 다음 문서를 업데이트하세요.

- `docs/index.md` — 지원 포맷 테이블에 추가
- `docs/formats/<format>.md` — 새 포맷 가이드 페이지 작성 (HWP/HWPX 참고)
- `mkdocs.yml` — 네비게이션에 추가

## 기여 워크플로

1. **이슈 생성** — 추가하려는 포맷에 대한 이슈를 먼저 생성하세요
2. **브랜치 생성** — `feature/add-<format>-parser` 형식으로 브랜치 생성
3. **구현** — 파서/Writer 구현 + 테스트 작성
4. **문서 업데이트** — 위 섹션 참고
5. **PR 생성** — 메인 브랜치로 Pull Request 생성
6. **리뷰** — CI 통과 및 코드 리뷰 진행

## 다음 단계

- [아키텍처](architecture.md) — 내부 구조 이해하기
- [API 레퍼런스](../api-reference.md) — Protocol 인터페이스 상세
