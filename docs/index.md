# ureca_document_parser

**Multi-format document parser and converter** — 한국어 워드프로세서(아래한글) HWP/HWPX 파일을 Markdown으로 변환합니다.

## 주요 기능

- **HWP v5 바이너리 파싱** — `olefile` 기반, 텍스트·표·이미지 추출
- **HWPX (OOXML) 파싱** — ZIP+XML 구조, 표준 라이브러리만 사용
- **Markdown 출력** — 헤딩, 리스트, 테이블 등 구조 보존
- **LangChain 연동** — RAG 파이프라인용 청크 분할 지원
- **확장 가능한 아키텍처** — Protocol 기반 파서/Writer 등록

## 퀵스타트

### 설치

```bash
pip install ureca_document_parser
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
