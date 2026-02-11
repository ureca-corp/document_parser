# Writer

[`Document`](models.md) 모델을 출력 포맷 문자열로 변환하는 Writer예요.

모든 Writer는 [`Writer` Protocol](registry.md)을 구현해요.

## Markdown Writer

Document를 GitHub Flavored Markdown으로 변환해요. 헤딩, 리스트, 테이블, 이미지 등 구조를 보존해요.

::: ureca_document_parser.writers.markdown.MarkdownWriter
    options:
      heading_level: 3
      members_order: source
