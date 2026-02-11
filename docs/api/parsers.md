# 파서 (HWP / HWPX)

문서 파일을 읽어 [`Document`](models.md) 모델로 변환하는 파서입니다.

모든 파서는 [`Parser` Protocol](registry.md)을 구현합니다.

## HWP 파서

HWP v5 바이너리 형식(아래한글 2007 이후)을 파싱합니다. 내부적으로 `olefile`을 사용하여 OLE2 컨테이너를 읽고, 레코드 스트림에서 텍스트와 표를 추출합니다.

::: ureca_document_parser.hwp.parser.HwpParser
    options:
      heading_level: 3
      members_order: source

## HWPX 파서

HWPX(한글 OOXML) 형식을 파싱합니다. ZIP 아카이브 내 XML 파일을 `xml.etree.ElementTree`로 처리합니다.

::: ureca_document_parser.hwpx.parser.HwpxParser
    options:
      heading_level: 3
      members_order: source
