# ureca_document_parser

한국어 워드프로세서(아래한글) HWP/HWPX 파일을 Markdown으로 변환하는 문서 파서예요.

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

convert("보고서.hwp", "보고서.md")
```

## 지원 포맷

| 입력 | 출력 |
|------|------|
| HWP (한글 v5 바이너리) | Markdown |
| HWPX (한글 OOXML) | Markdown |

## 다음 단계

- [시작하기](getting-started.md) — 설치부터 실전 활용까지
- [아키텍처](architecture.md) — 내부 구조와 설계 원칙
- [포맷 확장 가이드](adding-formats.md) — 새 파서/Writer 추가 방법
- [API 레퍼런스](api/index.md) — 전체 API 문서
