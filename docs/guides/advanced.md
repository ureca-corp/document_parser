# 고급 사용법

!!! warning "고급 사용자용"
    이 문서는 파싱 결과를 프로그래밍 방식으로 직접 제어하고 싶은 고급 사용자를 위한 가이드예요.
    대부분의 경우 [`convert()` 함수](python-api.md)만으로 충분해요.

파싱 결과를 세밀하게 제어하거나 문서 구조를 분석하고 싶을 때 내부 `Document` 모델을 직접 다룰 수 있어요.

## Document 모델 이해하기

`Document`는 파싱된 문서의 중간 표현(Intermediate Representation)이에요. 모든 파서는 이 모델을 생산하고, 모든 Writer는 이 모델을 소비해요.

```python
from ureca_document_parser.registry import get_registry

registry = get_registry()
doc = registry.parse("보고서.hwp")

print(type(doc))           # <class 'Document'>
print(len(doc.elements))   # 문서 요소 개수
print(doc.metadata)        # Metadata(title=..., author=..., ...)
```

### Document 구조

```python
from ureca_document_parser.models import Document

# Document는 두 부분으로 구성돼요
doc.elements   # list[DocumentElement] — 문서 내용
doc.metadata   # Metadata — 메타데이터
```

## 문서 요소 다루기

### 요소 타입 확인하기

문서는 여러 타입의 요소로 구성돼요.

```python
from ureca_document_parser.registry import get_registry
from ureca_document_parser.models import Paragraph, Table, ListItem, Image, HorizontalRule

registry = get_registry()
doc = registry.parse("보고서.hwp")

for element in doc.elements:
    if isinstance(element, Paragraph):
        print(f"문단: {element.text[:50]}...")
    elif isinstance(element, Table):
        print(f"표: {len(element.rows)}행 x {len(element.rows[0].cells)}열")
    elif isinstance(element, ListItem):
        print(f"리스트: {element.text}")
    elif isinstance(element, Image):
        print(f"이미지: {element.alt_text}")
    elif isinstance(element, HorizontalRule):
        print("구분선")
```

### 헤딩 추출하기

문서의 구조를 파악하려면 헤딩을 추출하면 돼요.

```python
from ureca_document_parser.registry import get_registry, Paragraph

registry = get_registry()
doc = registry.parse("보고서.hwp")

# 헤딩만 필터링
headings = [
    el for el in doc.elements
    if isinstance(el, Paragraph) and el.heading_level > 0
]

# 계층 구조 출력
for h in headings:
    indent = "  " * (h.heading_level - 1)
    print(f"{indent}{'#' * h.heading_level} {h.text}")
```

출력 예시:

```
# 프로젝트 개요
  ## 목표
  ## 범위
# 일정
  ## 1단계
  ## 2단계
```

### 본문 텍스트만 추출하기

헤딩과 표를 제외한 일반 문단만 추출할 수 있어요.

```python
from ureca_document_parser.registry import get_registry, Paragraph

registry = get_registry()
doc = registry.parse("보고서.hwp")

body_paragraphs = [
    el for el in doc.elements
    if isinstance(el, Paragraph) and el.heading_level == 0
]

body_text = "\n\n".join(p.text for p in body_paragraphs)
print(body_text)
```

### 표 데이터 추출하기

표를 2차원 배열로 변환할 수 있어요.

```python
from ureca_document_parser.registry import get_registry, Table, Paragraph

registry = get_registry()
doc = registry.parse("보고서.hwp")

# 모든 표 찾기
tables = [el for el in doc.elements if isinstance(el, Table)]

for i, table in enumerate(tables):
    print(f"\n=== 표 {i+1} ===")

    # 2차원 배열로 변환
    for row in table.rows:
        row_text = []
        for cell in row.cells:
            # 셀 내용을 텍스트로 결합
            cell_text = " ".join(
                item.text for item in cell.content if isinstance(item, Paragraph)
            )
            row_text.append(cell_text)
        print(" | ".join(row_text))
```

### 리스트 추출하기

```python
from ureca_document_parser.registry import get_registry, ListItem

registry = get_registry()
doc = registry.parse("보고서.hwp")

list_items = [el for el in doc.elements if isinstance(el, ListItem)]

for item in list_items:
    indent = "  " * item.level
    marker = "1." if item.ordered else "-"
    print(f"{indent}{marker} {item.text}")
```

## 메타데이터 활용하기

### 기본 메타데이터

```python
from ureca_document_parser.registry import get_registry

registry = get_registry()
doc = registry.parse("보고서.hwp")

print(f"제목: {doc.metadata.title}")
print(f"작성자: {doc.metadata.author}")
print(f"포맷: {doc.metadata.source_format}")
```

### 추가 메타데이터

`extra` 필드에 파서별 추가 정보가 담겨 있어요.

```python
print(f"추가 정보: {doc.metadata.extra}")
```

## 커스텀 변환 로직 작성하기

### 조건부 필터링

특정 조건에 맞는 요소만 선택할 수 있어요.

```python
from ureca_document_parser.registry import get_registry, Paragraph

registry = get_registry()
doc = registry.parse("보고서.hwp")

# "프로젝트"라는 단어가 포함된 문단만
project_paragraphs = [
    el for el in doc.elements
    if isinstance(el, Paragraph) and "프로젝트" in el.text
]

for p in project_paragraphs:
    print(p.text)
```

### 요소 재구성

요소 순서를 바꾸거나 특정 부분만 추출할 수 있어요.

```python
from ureca_document_parser.registry import get_registry, Paragraph, Table

registry = get_registry()
doc = registry.parse("보고서.hwp")

# 헤딩과 표만 추출 (본문 제외)
summary_elements = [
    el for el in doc.elements
    if (isinstance(el, Paragraph) and el.heading_level > 0) or isinstance(el, Table)
]

# 새 Document 생성
from ureca_document_parser.models import Document

summary_doc = Document(
    elements=summary_elements,
    metadata=doc.metadata,
)

# Markdown으로 변환
markdown = registry.write(summary_doc, "markdown")
print(markdown)
```

### 커스텀 출력 포맷

`Document` 모델을 직접 순회해서 원하는 포맷으로 변환할 수 있어요.

```python
from ureca_document_parser.registry import get_registry, Paragraph, Table, ListItem

registry = get_registry()
doc = registry.parse("보고서.hwp")

# HTML로 변환 (간단한 예시)
html_parts = ["<!DOCTYPE html>", "<html>", "<body>"]

for element in doc.elements:
    if isinstance(element, Paragraph):
        if element.heading_level > 0:
            tag = f"h{element.heading_level}"
            html_parts.append(f"<{tag}>{element.text}</{tag}>")
        else:
            html_parts.append(f"<p>{element.text}</p>")
    elif isinstance(element, ListItem):
        marker = "ol" if element.ordered else "ul"
        html_parts.append(f"<{marker}><li>{element.text}</li></{marker}>")

html_parts.extend(["</body>", "</html>"])
html = "\n".join(html_parts)
print(html)
```

## 통계 및 분석

### 문서 통계 내기

```python
from ureca_document_parser.registry import get_registry, Paragraph, Table, ListItem

registry = get_registry()
doc = registry.parse("보고서.hwp")

# 타입별 개수
paragraph_count = sum(1 for el in doc.elements if isinstance(el, Paragraph))
table_count = sum(1 for el in doc.elements if isinstance(el, Table))
list_count = sum(1 for el in doc.elements if isinstance(el, ListItem))

# 헤딩 레벨별 개수
heading_counts = {}
for el in doc.elements:
    if isinstance(el, Paragraph) and el.heading_level > 0:
        heading_counts[el.heading_level] = heading_counts.get(el.heading_level, 0) + 1

# 총 단어 수
total_words = sum(
    len(el.text.split())
    for el in doc.elements
    if isinstance(el, Paragraph)
)

print(f"문단: {paragraph_count}개")
print(f"표: {table_count}개")
print(f"리스트: {list_count}개")
print(f"헤딩: {heading_counts}")
print(f"총 단어 수: {total_words}개")
```

### 가장 긴 문단 찾기

```python
from ureca_document_parser.registry import get_registry, Paragraph

registry = get_registry()
doc = registry.parse("보고서.hwp")

paragraphs = [
    el for el in doc.elements
    if isinstance(el, Paragraph) and el.heading_level == 0
]

longest = max(paragraphs, key=lambda p: len(p.text))
print(f"가장 긴 문단 ({len(longest.text)}자):")
print(longest.text)
```

## 여러 문서 병합하기

여러 HWP 파일을 하나의 Document로 합칠 수 있어요.

```python
from pathlib import Path
from ureca_document_parser.registry import get_registry, Document, Paragraph, HorizontalRule

registry = get_registry()

all_elements = []

for file in Path("documents").glob("*.hwp"):
    doc = registry.parse(file)

    # 파일명을 헤딩으로 추가
    all_elements.append(Paragraph(text=file.stem, heading_level=1))

    # 문서 내용 추가
    all_elements.extend(doc.elements)

    # 구분선 추가
    all_elements.append(HorizontalRule())

# 병합된 Document 생성
merged = Document(elements=all_elements)

# Markdown으로 저장
markdown = registry.write(merged, "markdown")
Path("merged.md").write_text(markdown, encoding="utf-8")
```

## 에러 처리

### ParseError 상세 처리

```python
from ureca_document_parser.registry import get_registry, ParseError

registry = get_registry()

try:
    doc = registry.parse("손상된파일.hwp")
except ParseError as e:
    print(f"파싱 실패: {e}")
    print(f"에러 타입: {type(e).__name__}")
    # 로그 기록, 사용자 알림 등
```

### 일부 요소만 처리

파싱은 성공했지만 일부 요소가 누락될 수 있어요. 방어적으로 코딩하세요.

```python
from ureca_document_parser.registry import get_registry, Paragraph

registry = get_registry()
doc = registry.parse("복잡한문서.hwp")

# None 체크
for element in doc.elements:
    if isinstance(element, Paragraph):
        text = element.text or "(빈 문단)"
        print(text)
```

## 다음 단계

- [API 레퍼런스](../api-reference.md) — Document 모델 전체 스펙
- [아키텍처](../reference/architecture.md) — 내부 구조 이해하기
- [포맷 확장하기](../reference/extending.md) — 새 파서/Writer 추가하기
