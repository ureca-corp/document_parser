# CLAUDE.md

## Project Overview

`ureca_document_parser` — Multi-format document parser and converter. Parses Korean word processor (아래한글) HWP/HWPX files and outputs structured Markdown or LangChain Document chunks. Designed as a PyPI-distributable package with clean architecture for easy format extension.

## Commands

```bash
uv sync
uv run ureca_document_parser <file.hwp|file.hwpx> -o <output.md>
uv run ureca_document_parser --list-formats
uv run python -m ureca_document_parser <file.hwp> -o <output.md>
uv run pytest tests/ -v
uv build
```

## Architecture

**Pipeline**: Input file → Format registry → Parser → Document model → Writer → Output (or → TextSplitter → LangChain Documents)

```
src/ureca_document_parser/
├── __init__.py        # Public API (convert, convert_to_chunks, get_registry)
├── __main__.py        # python -m ureca_document_parser
├── cli.py             # CLI (argparse, registry 기반 자동 라우팅)
├── models.py          # Document model (Paragraph, Table, Image, ListItem, ...)
├── protocols.py       # Parser / Writer Protocol (구조적 서브타이핑)
├── registry.py        # FormatRegistry (확장자→파서, 포맷명→Writer 매핑, thread-safe singleton)
├── styles.py          # Shared heading patterns
├── hwp/
│   ├── __init__.py    # re-export HwpParser + low-level types
│   ├── parser.py      # HWP v5 binary parser (olefile) — orchestration
│   ├── records.py     # Binary record parsing (Record, RecordCursor, constants)
│   ├── text.py        # Character scanning & text extraction (CharInfo, BSTR)
│   └── tables.py      # 3-phase table extraction
├── hwpx/
│   ├── __init__.py    # re-export HwpxParser
│   └── parser.py      # HWPX parser (zipfile + xml.etree)
└── writers/
    └── markdown.py    # Markdown writer
```

### Key modules

- **`protocols.py`** — `Parser` / `Writer` Protocol. No inheritance needed; match static method signatures.
- **`registry.py`** — `FormatRegistry` maps extensions→parsers, format names→writers. Thread-safe singleton via `get_registry()`.
- **`models.py`** — Shared document model. `Document` = `list[DocumentElement]` + `Metadata`. `ParseError` for parser failures.
- **`hwp/`** — HWP v5 binary parser split into `records.py` (record stream), `text.py` (char extraction), `tables.py` (table parsing), `parser.py` (orchestration).
- **`hwpx/parser.py`** — HWPX (ZIP+XML) parser using stdlib `xml.etree`.
- **`writers/markdown.py`** — Converts `Document` to Markdown. Groups consecutive `ListItem`s into single blocks.

### Library usage

```python
from ureca_document_parser.hwp import HwpParser
from ureca_document_parser.writers.markdown import MarkdownWriter
doc = HwpParser.parse("document.hwp")
md = MarkdownWriter.write(doc)

from ureca_document_parser import convert
convert("document.hwp", "output.md")

from ureca_document_parser import convert_to_chunks
chunks = convert_to_chunks("document.hwp", chunk_size=1000, chunk_overlap=200)
```

## Testing

```bash
uv run pytest tests/ -v              # run all tests
uv run pytest tests/ --cov           # with coverage
```

Tests cover: models, registry, CLI, HWP parser (unit + integration), HWPX parser, Markdown writer.

## Adding New Formats

See `docs/adding-formats.md`. Create a parser/writer class matching the Protocol, register in `registry.py:_auto_register()`.

## Dependencies

Core: `olefile` (BSD). Optional: `langchain-text-splitters`+`langchain-core` (chunking), `pymupdf` (PDF), `pillow`+`pytesseract` (OCR). Dev: `pytest`, `pytest-cov`, `mypy`, `ruff`.

## Documentation

### Structure

```
docs/
├── index.md              # 홈 — 퀵스타트, 주요 기능
├── getting-started.md    # 설치, CLI, Python API 사용법
├── architecture.md       # 파이프라인, 모듈 의존성, Mermaid 다이어그램
├── adding-formats.md     # 새 Parser/Writer 추가 가이드 (기여자용)
└── api/
    ├── index.md          # API 개요 + 최상위 API (mkdocstrings 자동 생성)
    ├── models.md         # Document 모델 (mkdocstrings 자동 생성)
    ├── parsers.md        # HWP/HWPX 파서 (mkdocstrings 자동 생성)
    ├── writers.md        # Markdown Writer (mkdocstrings 자동 생성)
    └── registry.md       # FormatRegistry + Protocol (mkdocstrings 자동 생성)
```

### Writing style

- 말투: es-toolkit 스타일 친근한 존댓말 (`~예요`, `~해요`, `~돼요`)
- 관점: **외부 프로젝트에 설치해서 쓰는 사용자** 기준. 내부 소스코드를 복붙하지 않는다.
- CLI 예제는 반드시 `uv run ureca_document_parser ...` 형태로 작성한다.
- 예제 파일명은 실제 사용 시나리오 기반 (예: `보고서.hwp`, `제안서.hwpx`)
- `docs/api/` 하위 파일은 `mkdocstrings`가 docstring에서 자동 생성하므로 설명문만 작성한다.
- `docs/adding-formats.md`만 기여자(contributor) 관점으로 작성한다.
- Mermaid 다이어그램 사용 가능 (mkdocs.yml에 설정 완료)
- MkDocs admonition 사용 가능: `!!! note`, `!!! info`, `!!! warning`

### Build & preview

```bash
uv sync --extra docs                    # 문서 의존성 설치
uv run mkdocs serve                     # http://127.0.0.1:8000 로컬 미리보기
uv run mkdocs build                     # site/ 디렉토리에 정적 파일 빌드
```

### Deploy

배포는 자동이다. `main` 브랜치에 push하면 `.github/workflows/docs.yml`이 실행되어 GitHub Pages에 배포된다.

- 워크플로우: `mkdocs gh-deploy --force` → `gh-pages` 브랜치에 push
- Pages 설정: Source = `gh-pages` branch (GitHub Settings → Pages)
- URL: https://ureca-corp.github.io/document_parser/

수동 배포가 필요한 경우:

```bash
uv run mkdocs gh-deploy --force
```

### Navigation

페이지를 추가/삭제하면 `mkdocs.yml`의 `nav:` 섹션을 함께 수정해야 한다.

## CI

GitHub Actions (`.github/workflows/ci.yml`) runs on push/PR to main: tests on Python 3.12 + 3.13, plus ruff lint/format checks.
