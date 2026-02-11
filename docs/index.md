# ureca_document_parser

한국어 워드프로세서(아래한글) HWP/HWPX 파일을 Markdown으로 변환하는 현대적인 문서 파서예요.

## 주요 기능

- **HWP v5 바이너리 파싱** — `olefile` 기반으로 텍스트, 표, 이미지를 추출해요
- **HWPX (OOXML) 파싱** — ZIP+XML 구조를 표준 라이브러리만으로 처리해요
- **Markdown 출력** — 헤딩, 리스트, 테이블 등 문서 구조를 보존해요
- **LangChain 연동** — RAG 파이프라인용 청크 분할을 지원해요
- **확장 가능한 아키텍처** — Protocol 기반으로 새 파서/Writer를 쉽게 등록할 수 있어요

## 퀵스타트

### 설치

```bash
uv add ureca_document_parser
```

### CLI 사용

```bash
ureca_document_parser document.hwp -o output.md
```

### 라이브러리 사용

```python
from ureca_document_parser import convert

# 파일 변환
convert("document.hwp", "output.md")

# LangChain 청크 분할
from ureca_document_parser import convert_to_chunks

chunks = convert_to_chunks("document.hwp", chunk_size=1000, chunk_overlap=200)
```

## 지원 포맷

| 입력 | 출력 |
|------|------|
| HWP (한글 v5 바이너리) | Markdown |
| HWPX (한글 OOXML) | Markdown |

## 다음 단계

- [시작하기](getting-started.md) — 설치 및 상세 사용법
- [아키텍처](architecture.md) — 내부 구조와 설계 원칙
- [포맷 확장](adding-formats.md) — 새 파서/Writer 추가 가이드
- [API 레퍼런스](api/index.md) — 전체 API 문서
