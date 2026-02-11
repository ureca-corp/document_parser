# ureca_document_parser

한국어 워드프로세서(아래한글) 문서를 Markdown으로 변환하는 다중 포맷 파서예요.

## 주요 기능

- **HWP v5 바이너리 파싱** — 텍스트, 표, 헤딩 구조를 추출해요
- **HWPX (OOXML) 파싱** — ZIP+XML 기반의 최신 한글 포맷을 지원해요
- **Markdown 출력** — 헤딩, 리스트, 테이블 등 문서 구조를 보존해요
- **LangChain 연동** — RAG 파이프라인에 바로 연결할 수 있어요

## 퀵스타트

### 설치

```bash
uv add ureca_document_parser
```

### CLI로 변환하기

```bash
uv run ureca_document_parser 보고서.hwp -o 보고서.md
```

### Python에서 사용하기

```python
from ureca_document_parser import convert

# 파일로 저장
convert("보고서.hwp", "보고서.md")

# 또는 문자열로 반환
markdown = convert("보고서.hwp")
```

### LangChain과 함께 사용하기

```python
from ureca_document_parser import convert

# RAG 파이프라인에 바로 사용 가능한 청크 생성
chunks = convert("보고서.hwp", chunks=True, chunk_size=1000, chunk_overlap=200)
```

## 지원 포맷

| 입력 포맷 | 설명 | 문서 |
|----------|------|------|
| **HWP** | 아래한글 v5 바이너리 형식 (2007 이후) | [자세히 보기](formats/hwp.md) |
| **HWPX** | 아래한글 OOXML 형식 (ZIP+XML) | [자세히 보기](formats/hwpx.md) |

| 출력 포맷 | 설명 |
|----------|------|
| **Markdown** | GitHub Flavored Markdown |

## 다음 단계

- [설치 방법](installation.md) — 기본 설치부터 선택적 의존성까지
- [CLI 사용법](guides/cli.md) — 명령줄에서 파일 변환하기
- [Python API 사용법](guides/python-api.md) — 코드에서 파서 활용하기
- [LangChain 연동](guides/langchain.md) — RAG 파이프라인 구축하기
- [API 레퍼런스](api-reference.md) — 전체 API 문서

## 라이선스

MIT License

## 기여하기

버그 리포트나 기능 제안은 [GitHub Issues](https://github.com/ureca-corp/document_parser/issues)로 부탁드려요.
