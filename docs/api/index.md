# API 레퍼런스

`ureca_document_parser`의 공개 API 문서예요.

## 모듈 구조

| 모듈 | 설명 |
|------|------|
| [`ureca_document_parser.models`](models.md) | Document 모델 — 파서와 Writer가 공유하는 데이터 구조 |
| [`ureca_document_parser.hwp`](parsers.md#hwp-파서) | HWP v5 바이너리 파서 |
| [`ureca_document_parser.hwpx`](parsers.md#hwpx-파서) | HWPX (ZIP+XML) 파서 |
| [`ureca_document_parser.writers.markdown`](writers.md) | Markdown Writer |
| [`ureca_document_parser.registry`](registry.md) | FormatRegistry — 파서/Writer 자동 라우팅 |

## 최상위 API

::: ureca_document_parser
    options:
      members:
        - convert
        - convert_to_chunks
        - get_registry
      show_root_heading: false
      heading_level: 3
