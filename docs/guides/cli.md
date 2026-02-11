# CLI 사용법

명령줄(CLI)에서 `ureca_document_parser`를 사용해서 파일을 빠르게 변환할 수 있어요.

## 기본 사용법

### 파일 변환하기

```bash
uv run ureca_document_parser 보고서.hwp -o 보고서.md
```

HWPX 파일도 동일하게 동작해요.

```bash
uv run ureca_document_parser 제안서.hwpx -o 제안서.md
```

### 표준 출력으로 결과 보기

`-o` 옵션을 생략하면 변환 결과가 터미널에 출력돼요.

```bash
uv run ureca_document_parser 보고서.hwp
```

파이프와 함께 사용할 수도 있어요.

```bash
uv run ureca_document_parser 보고서.hwp | less
uv run ureca_document_parser 보고서.hwp > 출력.md
```

## 옵션

### 출력 포맷 지정

`-f` 또는 `--format` 옵션으로 출력 포맷을 지정할 수 있어요. 현재는 `markdown`만 지원해요.

```bash
uv run ureca_document_parser 보고서.hwp -f markdown -o 보고서.md
```

### 지원 포맷 확인

```bash
uv run ureca_document_parser --list-formats
```

출력 예시:

```
Supported input formats:
  .hwp  - HWP v5 binary format
  .hwpx - HWPX (OOXML) format

Supported output formats:
  markdown (.md)
```

### 도움말 보기

```bash
uv run ureca_document_parser --help
```

## 실전 예시

### 여러 파일 일괄 변환

Bash에서 와일드카드를 사용해서 여러 파일을 변환할 수 있어요.

```bash
for file in documents/*.hwp; do
  uv run ureca_document_parser "$file" -o "output/$(basename "$file" .hwp).md"
done
```

### 디렉토리 구조 유지하며 변환

`find` 명령어와 함께 사용하면 서브디렉토리까지 재귀적으로 변환할 수 있어요.

```bash
find documents -name "*.hwp" -o -name "*.hwpx" | while read file; do
  output="output/${file#documents/}"
  output="${output%.*}.md"
  mkdir -p "$(dirname "$output")"
  uv run ureca_document_parser "$file" -o "$output"
  echo "변환 완료: $file → $output"
done
```

### 조건부 변환 (이미 존재하면 건너뛰기)

```bash
for file in documents/*.hwp; do
  output="output/$(basename "$file" .hwp).md"
  if [ ! -f "$output" ]; then
    uv run ureca_document_parser "$file" -o "$output"
    echo "변환: $file"
  else
    echo "건너뛰기: $file (이미 존재)"
  fi
done
```

## 에러 처리

### 파일을 찾을 수 없을 때

```bash
$ uv run ureca_document_parser 없는파일.hwp
Error: File not found: 없는파일.hwp
```

### 지원하지 않는 확장자

```bash
$ uv run ureca_document_parser 문서.docx
Error: Unsupported file format: .docx
Supported formats: .hwp, .hwpx
```

### 파싱 에러

파일이 손상되었거나 올바른 형식이 아닐 때:

```bash
$ uv run ureca_document_parser 손상된파일.hwp
Error: Failed to parse 손상된파일.hwp: Invalid HWP signature
```

## 다음 단계

- [Python API 가이드](python-api.md) — 코드에서 더 유연하게 사용하기
- [LangChain 연동](langchain.md) — RAG 파이프라인 구축하기
