# Writer

[`Document`](models.md) 모델을 출력 포맷 문자열로 변환하는 Writer예요. 모든 Writer는 [`Writer` Protocol](registry.md#protocol)을 구현해요.

| 포맷 이름 | Writer 클래스 | 확장자 |
|-----------|--------------|--------|
| `markdown` | `MarkdownWriter` | `.md` |

## Markdown Writer

`Document`를 GitHub Flavored Markdown으로 변환해요. 헤딩, 리스트, 테이블, 이미지 등 구조를 보존해요.

```python
from ureca_document_parser import get_registry

registry = get_registry()
doc = registry.parse("보고서.hwp")
md_text = registry.write(doc, "markdown")
```

::: ureca_document_parser.writers.markdown.MarkdownWriter
    options:
      heading_level: 3
      members_order: source
