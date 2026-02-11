# API 레퍼런스

`ureca_document_parser`의 공개 API 문서예요.

## 최상위 API

| 함수 | 설명 |
|------|------|
| [`convert()`](#convert) | 파일을 변환해서 저장해요 |
| [`convert_to_chunks()`](#convert_to_chunks) | 파일을 파싱해서 LangChain 청크로 분할해요 |
| [`get_registry()`](#get_registry) | 포맷 레지스트리 싱글톤을 반환해요 |

::: ureca_document_parser
    options:
      members:
        - convert
        - convert_to_chunks
        - get_registry
      show_root_heading: false
      heading_level: 3

## 파서

문서 파일을 읽어 `Document` 모델로 변환하는 클래스예요. 확장자에 따라 자동으로 라우팅돼요.

| 확장자 | 파서 클래스 | 설명 |
|--------|------------|------|
| `.hwp` | [`HwpParser`](parsers.md#hwp-파서) | 아래한글 v5 바이너리 형식 |
| `.hwpx` | [`HwpxParser`](parsers.md#hwpx-파서) | 아래한글 OOXML (ZIP+XML) 형식 |

## Writer

`Document` 모델을 출력 포맷 문자열로 변환하는 클래스예요.

| 포맷 이름 | Writer 클래스 | 확장자 | 설명 |
|-----------|--------------|--------|------|
| `markdown` | [`MarkdownWriter`](writers.md#markdown-writer) | `.md` | GitHub Flavored Markdown |

## 모델 및 레지스트리

| 모듈 | 설명 |
|------|------|
| [`models`](models.md) | `Document`, `Paragraph`, `Table` 등 공유 데이터 모델 |
| [`registry`](registry.md) | `FormatRegistry` — 파서/Writer 자동 라우팅 |
| [`protocols`](registry.md#protocol) | `Parser` / `Writer` Protocol 인터페이스 |
