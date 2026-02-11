# 시작하기

## 설치

### 기본 설치

```bash
uv add ureca_document_parser
```

### 선택적 의존성

필요한 기능에 따라 추가 의존성을 설치할 수 있어요.

```bash
# LangChain 청크 분할
uv add "ureca_document_parser[langchain]"

# PDF 파싱 지원
uv add "ureca_document_parser[pdf]"

# OCR 지원
uv add "ureca_document_parser[ocr]"

# 모든 기능
uv add "ureca_document_parser[all]"
```

## CLI 사용법

### 기본 변환

HWP 또는 HWPX 파일을 Markdown으로 변환할 수 있어요.

```bash
uv run ureca_document_parser 보고서.hwp -o 보고서.md
uv run ureca_document_parser 제안서.hwpx -o 제안서.md
```

`-o` 옵션을 생략하면 결과가 표준 출력으로 나와요.

```bash
uv run ureca_document_parser 보고서.hwp
```

### 출력 포맷 지정

`-f` 옵션으로 출력 포맷을 지정할 수 있어요. 현재는 `markdown`이 기본값이에요.

```bash
uv run ureca_document_parser 보고서.hwp -f markdown -o 보고서.md
```

### 지원 포맷 확인

```bash
uv run ureca_document_parser --list-formats
```

## Python API 사용법

### 파일 변환

가장 간단한 방법이에요. 입력 파일 경로와 출력 파일 경로만 전달하면 돼요.

```python
from ureca_document_parser import convert

convert("보고서.hwp", "output/보고서.md")
```

출력 디렉토리가 없으면 자동으로 생성해요.

### 변환 결과를 문자열로 받기

파일로 저장하지 않고 Markdown 문자열을 직접 받고 싶을 때 사용해요.

```python
from ureca_document_parser import get_registry

registry = get_registry()
doc = registry.parse("보고서.hwp")
md_text = registry.write(doc, "markdown")

print(md_text)
```

### Document 모델 활용

파싱 결과를 프로그래밍 방식으로 처리하고 싶을 때 `Document` 모델을 직접 다룰 수 있어요.

```python
from ureca_document_parser import get_registry
from ureca_document_parser.models import Paragraph, Table

registry = get_registry()
doc = registry.parse("보고서.hwp")

# 헤딩만 추출
headings = [
    el for el in doc.elements
    if isinstance(el, Paragraph) and el.heading_level > 0
]
for h in headings:
    print(f"{'#' * h.heading_level} {h.text}")

# 테이블 개수 확인
tables = [el for el in doc.elements if isinstance(el, Table)]
print(f"테이블 {len(tables)}개 발견")
```

### LangChain 연동

RAG 파이프라인에 바로 연결할 수 있는 LangChain Document 리스트를 생성해요.

```python
from ureca_document_parser import convert_to_chunks

chunks = convert_to_chunks(
    "보고서.hwp",
    chunk_size=1000,
    chunk_overlap=200,
)

for chunk in chunks:
    print(chunk.page_content[:100])
    print(chunk.metadata)
    # {'source': '보고서.hwp', 'format': 'hwp'}
```

!!! note
    `convert_to_chunks`를 사용하려면 `langchain` 추가 의존성이 필요해요.

    ```bash
    uv add "ureca_document_parser[langchain]"
    ```

### 여러 파일 일괄 변환

```python
from pathlib import Path
from ureca_document_parser import convert

hwp_files = Path("documents").glob("*.hwp")

for hwp_file in hwp_files:
    output = Path("output") / hwp_file.with_suffix(".md").name
    convert(hwp_file, output)
    print(f"변환 완료: {hwp_file.name} → {output.name}")
```

## 개발 환경 설정

라이브러리 자체를 수정하거나 기여하고 싶다면 다음과 같이 설정하세요.

```bash
git clone https://github.com/ureca-corp/document_parser.git
cd document_parser
uv sync --extra dev
```

테스트 실행은 다음과 같이 해요.

```bash
uv run pytest tests/ -v
```
