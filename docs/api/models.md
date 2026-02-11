# Document 모델

파서와 Writer가 공유하는 중간 표현(IR) 데이터 모델이에요. 모든 파서는 `Document`를 생산하고, 모든 Writer는 `Document`를 소비해요.

## 구조 개요

```
Document
├── metadata: Metadata
└── elements: list[DocumentElement]
    ├── Paragraph      — 텍스트 문단 또는 헤딩
    ├── Table          — 행/열 기반 표 (중첩 지원)
    ├── Image          — 이미지 (OCR 텍스트 포함 가능)
    ├── ListItem       — 순서 있는/없는 리스트 항목
    ├── Link           — 하이퍼링크
    └── HorizontalRule — 수평선
```

## 클래스 상세

::: ureca_document_parser.models
    options:
      heading_level: 3
      members_order: source
