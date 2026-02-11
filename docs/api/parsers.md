# 파서

문서 파일을 읽어 [`Document`](models.md) 모델로 변환하는 파서예요. 모든 파서는 [`Parser` Protocol](registry.md#protocol)을 구현해요.

| 확장자 | 파서 클래스 | 포맷 | 핵심 의존성 |
|--------|------------|------|------------|
| `.hwp` | `HwpParser` | 아래한글 v5 바이너리 | [olefile](https://olefile.readthedocs.io/) |
| `.hwpx` | `HwpxParser` | 아래한글 OOXML (ZIP+XML) | 표준 라이브러리 |

## HWP 파서

HWP v5 바이너리 형식(아래한글 2007 이후)을 파싱해요. 내부적으로 [olefile](https://olefile.readthedocs.io/)을 사용해서 OLE2 컨테이너를 읽고, 레코드 스트림에서 텍스트와 표를 추출해요.

```python
from ureca_document_parser import get_registry

doc = get_registry().parse("보고서.hwp")
```

::: ureca_document_parser.hwp.parser.HwpParser
    options:
      heading_level: 3
      members_order: source

## HWPX 파서

HWPX(한글 OOXML) 형식을 파싱해요. ZIP 아카이브 내 XML 파일을 표준 라이브러리 `xml.etree.ElementTree`로 처리하므로 추가 의존성이 필요 없어요.

```python
from ureca_document_parser import get_registry

doc = get_registry().parse("제안서.hwpx")
```

::: ureca_document_parser.hwpx.parser.HwpxParser
    options:
      heading_level: 3
      members_order: source
