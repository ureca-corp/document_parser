# Writer

[`Document`](models.md) 모델을 출력 포맷 문자열로 변환하는 Writer입니다.

모든 Writer는 [`Writer` Protocol](registry.md)을 구현합니다.

## Markdown Writer

Document를 GitHub Flavored Markdown으로 변환합니다. 헤딩, 리스트, 테이블, 이미지 등 구조를 보존합니다.

::: ureca_document_parser.writers.markdown.MarkdownWriter
    options:
      heading_level: 3
      members_order: source
