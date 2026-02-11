# Python API 사용법

Python 코드에서 `ureca_document_parser`를 사용하는 방법을 알아봐요.

## 기본 사용법

### 파일로 저장

가장 간단한 방법이에요. 입력 파일과 출력 파일 경로만 지정하면 돼요.

```python
from ureca_document_parser import convert

# HWP → Markdown 파일로 저장
convert("보고서.hwp", "output/보고서.md")

# HWPX도 동일하게 동작
convert("제안서.hwpx", "output/제안서.md")
```

출력 디렉토리가 없으면 자동으로 생성돼요.

```python
convert("문서.hwp", "deep/nested/directory/문서.md")
# deep/nested/directory/ 디렉토리가 자동 생성됨
```

### 문자열로 반환

파일로 저장하지 않고 Markdown 문자열을 직접 받고 싶을 때는 `output_path`를 생략하세요.

```python
from ureca_document_parser import convert

# Markdown 문자열 반환
markdown = convert("보고서.hwp")
print(markdown)

# 다른 용도로 사용
processed = markdown.replace("구버전", "신버전")
```

### 출력 포맷 지정

`format` 매개변수로 출력 포맷을 지정할 수 있어요. (기본값: `"markdown"`)

```python
convert("보고서.hwp", "보고서.md", format="markdown")
```

## 사용 패턴 요약

`convert()` 함수는 매개변수 조합에 따라 다양한 방식으로 사용할 수 있어요. 상황에 맞는 패턴을 선택하세요.

| 용도 | 코드 예시 | 반환값 |
|------|----------|--------|
| **파일로 바로 저장** | `convert("보고서.hwp", "보고서.md")` | `None` |
| **문자열로 받아서 처리** | `markdown = convert("보고서.hwp")` | `str` (Markdown 텍스트) |
| **여러 파일 결합** | `md = convert("part1.hwp")`<br>`combined = md + convert("part2.hwp")` | `str` |
| **파싱 후 조건부 저장** | `md = convert("문서.hwp")`<br>`if "키워드" in md:`<br>`    Path("out.md").write_text(md)` | `str` |
| **포맷 명시** | `convert("문서.hwp", "문서.md", format="markdown")` | `None` |
| **디렉토리 자동 생성** | `convert("문서.hwp", "a/b/c/문서.md")` | `None` (경로 자동 생성) |

!!! tip "반환값 타입 구분하기"
    - `output_path`를 지정하면 → **파일 저장** + `None` 반환
    - `output_path`를 생략하면 → **문자열 반환** (`str`)

    문자열로 받으면 추가 처리가 가능하고, 파일로 저장하면 코드가 간결해져요.

## 실전 예시

### 여러 파일 일괄 변환

```python
from pathlib import Path
from ureca_document_parser import convert

# HWP 파일만
hwp_files = Path("documents").glob("*.hwp")
for hwp_file in hwp_files:
    output = Path("output") / hwp_file.with_suffix(".md").name
    convert(hwp_file, output)
    print(f"✓ {hwp_file.name} → {output.name}")

# HWP + HWPX 모두
all_files = list(Path("documents").glob("*.hwp")) + list(Path("documents").glob("*.hwpx"))
for file in all_files:
    output = Path("output") / file.with_suffix(".md").name
    convert(file, output)
    print(f"✓ {file.name}")
```

### 재귀적 변환 (서브디렉토리 포함)

```python
from pathlib import Path
from ureca_document_parser import convert

def convert_directory(input_dir: Path, output_dir: Path):
    """디렉토리 구조를 유지하며 모든 HWP/HWPX 파일을 변환"""
    for file in input_dir.rglob("*"):
        if file.suffix in [".hwp", ".hwpx"]:
            # 상대 경로 유지
            relative_path = file.relative_to(input_dir)
            output_path = output_dir / relative_path.with_suffix(".md")

            # 출력 디렉토리 생성
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # 변환
            convert(file, output_path)
            print(f"✓ {relative_path}")

convert_directory(Path("documents"), Path("output"))
```

### 조건부 변환 (이미 존재하면 건너뛰기)

```python
from pathlib import Path
from ureca_document_parser import convert

def convert_if_needed(input_file: Path, output_file: Path):
    """출력 파일이 없거나 입력 파일이 더 최신일 때만 변환"""
    if not output_file.exists() or input_file.stat().st_mtime > output_file.stat().st_mtime:
        convert(input_file, output_file)
        print(f"✓ 변환: {input_file.name}")
    else:
        print(f"- 건너뛰기: {input_file.name}")

for hwp_file in Path("documents").glob("*.hwp"):
    output = Path("output") / hwp_file.with_suffix(".md").name
    convert_if_needed(hwp_file, output)
```

### 메타데이터 추출

```python
from ureca_document_parser import get_registry

registry = get_registry()
doc = registry.parse("보고서.hwp")

print(f"제목: {doc.metadata.title}")
print(f"작성자: {doc.metadata.author}")
print(f"포맷: {doc.metadata.source_format}")
print(f"추가 정보: {doc.metadata.extra}")
```

### 여러 문서 결합

여러 파일을 파싱해서 하나로 합칠 수 있어요.

```python
from ureca_document_parser import convert

# 여러 파일을 파싱해서 하나로 합치기
documents = []
for file in ["part1.hwp", "part2.hwp", "part3.hwp"]:
    markdown = convert(file)  # 문자열로 반환
    documents.append(markdown)

# 결합
combined = "\n\n---\n\n".join(documents)
print(combined)

# 하나의 파일로 저장
from pathlib import Path
Path("combined.md").write_text(combined, encoding="utf-8")
```

## 에러 처리

### ParseError 처리

파싱에 실패하면 `ParseError`가 발생해요.

```python
from ureca_document_parser import get_registry
from ureca_document_parser import ParseError

registry = get_registry()

try:
    doc = registry.parse("손상된파일.hwp")
except ParseError as e:
    print(f"파싱 실패: {e}")
    # 로그 기록, 사용자 알림 등
```

### 일괄 변환 시 에러 처리

```python
from pathlib import Path
from ureca_document_parser import convert
from ureca_document_parser import ParseError

failed_files = []

for hwp_file in Path("documents").glob("*.hwp"):
    try:
        output = Path("output") / hwp_file.with_suffix(".md").name
        convert(hwp_file, output)
        print(f"✓ {hwp_file.name}")
    except ParseError as e:
        print(f"✗ {hwp_file.name}: {e}")
        failed_files.append(hwp_file)

if failed_files:
    print(f"\n실패한 파일 {len(failed_files)}개:")
    for file in failed_files:
        print(f"  - {file}")
```

## 다음 단계

- [고급 사용법](advanced.md) — Document 모델 직접 다루기
- [LangChain 연동](langchain.md) — RAG 파이프라인 구축하기
- [API 레퍼런스](../api-reference.md) — 전체 API 문서
