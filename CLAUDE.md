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

## CI

GitHub Actions (`.github/workflows/ci.yml`) runs on push/PR to main: tests on Python 3.12 + 3.13, plus ruff lint/format checks.
