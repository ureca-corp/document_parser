# API 레퍼런스

`ureca_document_parser`의 공개 API 문서예요.

## convert()

파일을 변환해요. 용도에 따라 다양한 방식으로 사용할 수 있어요.

::: ureca_document_parser.convert
    options:
      heading_level: 3
      show_source: false

### 매개변수

| 매개변수 | 타입 | 기본값 | 설명 |
|---------|------|--------|------|
| `input_path` | `str \| Path` | (필수) | 변환할 입력 파일 경로 (.hwp, .hwpx, .pdf) |
| `output_path` | `str \| Path \| None` | `None` | 출력 파일 경로. `None`이면 문자열로 반환. `chunks=True`면 무시됨 |
| `format` | `str` | `"markdown"` | 출력 포맷 이름 |
| `chunks` | `bool` | `False` | `True`면 LangChain Document 청크로 반환 (`langchain` 추가 의존성 필요) |
| `chunk_size` | `int` | `1000` | 각 청크의 최대 문자 수 (`chunks=True`일 때만 사용) |
| `chunk_overlap` | `int` | `200` | 인접 청크 간 중복 문자 수 (`chunks=True`일 때만 사용) |

### 반환값

| 상황 | 반환 타입 | 설명 |
|------|----------|------|
| `chunks=True` | `list[LCDocument]` | LangChain Document 청크 리스트 |
| `chunks=False`, `output_path=None` | `str` | 변환된 Markdown 문자열 |
| `chunks=False`, `output_path` 지정 | `None` | 파일에 저장됨 |

### 사용 예시

**1. 파일로 저장**

```python
from ureca_document_parser import convert

convert("보고서.hwp", "보고서.md")
```

**2. 문자열로 반환**

```python
from ureca_document_parser import convert

markdown = convert("보고서.hwp")
print(markdown)
```

**3. LangChain 청크로 반환**

!!! note "선택적 의존성 필요"
    `chunks=True`를 사용하려면 `langchain` 추가 의존성이 필요해요.

    ```bash
    uv add "ureca_document_parser[langchain]"
    ```

```python
from ureca_document_parser import convert

# 기본 설정
chunks = convert("보고서.hwp", chunks=True)

# 청크 크기 커스텀
chunks = convert("보고서.hwp", chunks=True, chunk_size=500, chunk_overlap=100)

for chunk in chunks:
    print(chunk.page_content)
    print(chunk.metadata)
```

---


## ParseError

파싱 실패 시 발생하는 예외예요.

::: ureca_document_parser.ParseError
    options:
      heading_level: 3
      show_source: false

### 사용 예시

```python
from ureca_document_parser import convert, ParseError

try:
    convert("손상된파일.hwp", "출력.md")
except ParseError as e:
    print(f"파싱 실패: {e}")
```

---

## 더 알아보기

- [Python API 가이드](guides/python-api.md) — 기본 사용법
- [LangChain 연동](guides/langchain.md) — RAG 파이프라인 구축
- [고급 사용법](guides/advanced.md) — 내부 Document 모델 직접 다루기
