# Document 모델

파서와 Writer가 공유하는 중간 표현(IR) 데이터 모델입니다. 모든 파서는 `Document`를 생산하고, 모든 Writer는 `Document`를 소비합니다.

```
Document
├── metadata: Metadata
└── elements: list[DocumentElement]
    ├── Paragraph
    ├── Table (rows → cells → paragraphs)
    ├── Image
    ├── ListItem
    ├── Link
    └── HorizontalRule
```

::: ureca_document_parser.models
    options:
      heading_level: 2
      members_order: source
