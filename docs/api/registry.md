# FormatRegistry

파서와 Writer를 중앙에서 관리하는 레지스트리예요. 파일 확장자 기반으로 파서를 자동 라우팅하고, 포맷 이름으로 Writer를 선택해요.

## Protocol

파서와 Writer가 구현해야 하는 인터페이스예요. 상속 없이 메서드 시그니처만 맞추면 돼요.

::: ureca_document_parser.protocols.Parser
    options:
      heading_level: 3

::: ureca_document_parser.protocols.Writer
    options:
      heading_level: 3

## 레지스트리

::: ureca_document_parser.registry
    options:
      heading_level: 3
      members_order: source
