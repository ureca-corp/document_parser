# 시작하기

## 설치

### 기본 설치

```bash
pip install ureca_document_parser
```

### 선택적 의존성

```bash
# LangChain 청크 분할
pip install ureca_document_parser[langchain]

# PDF 파싱 지원
pip install ureca_document_parser[pdf]

# OCR 지원
pip install ureca_document_parser[ocr]

# 모든 기능
pip install ureca_document_parser[all]
```

### 개발 환경

```bash
git clone https://github.com/ureca-team/document_parser.git
cd document_parser
uv sync --extra dev
```

## CLI 사용법

### 기본 변환

```bash
ureca_document_parser document.hwp -o output.md
ureca_document_parser document.hwpx -o output.md
```

### 지원 포맷 확인

```bash
ureca_document_parser --list-formats
```

### python -m 실행

```bash
python -m ureca_document_parser document.hwp -o output.md
```

## 라이브러리 사용법

### 간편 변환 (High-level)

```python
from ureca_document_parser import convert

convert("document.hwp", "output.md")
```

### 레지스트리 기반 (Mid-level)

```python
from ureca_document_parser import get_registry

registry = get_registry()
doc = registry.parse("document.hwp")
md = registry.write(doc, "markdown")
```

### 직접 파서/Writer 사용 (Low-level)

```python
from ureca_document_parser.hwp import HwpParser
from ureca_document_parser.writers.markdown import MarkdownWriter

doc = HwpParser.parse("document.hwp")
md = MarkdownWriter.write(doc)
```

### LangChain 청크 분할

RAG 파이프라인에서 사용할 수 있는 LangChain Document 리스트를 생성합니다.

```python
from ureca_document_parser import convert_to_chunks

chunks = convert_to_chunks(
    "document.hwp",
    chunk_size=1000,
    chunk_overlap=200,
)

for chunk in chunks:
    print(chunk.page_content[:100])
    print(chunk.metadata)
```

!!! note
    `convert_to_chunks`를 사용하려면 `langchain` 추가 의존성이 필요합니다:
    `pip install ureca_document_parser[langchain]`
