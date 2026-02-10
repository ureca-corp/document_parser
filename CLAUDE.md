# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

`docparser` — Multi-format document parser and converter. Parses Korean word processor (아래한글) HWP/HWPX files and outputs structured Markdown. Designed as a PyPI-distributable package with clean architecture for easy format extension.

## Commands

```bash
# Install dependencies (uses uv, not pip)
uv sync

# Run converter (CLI)
uv run docparser <file.hwp|file.hwpx> -o <output.md>
uv run docparser <file.hwp>                          # stdout
uv run docparser --list-formats                      # 지원 형식 출력

# Run as module
uv run python -m docparser <file.hwp> -o <output.md>

# Build package
uv build
```

## Architecture

**Pipeline**: Input file → Format registry → Parser → Document model → Writer → Output

```
src/docparser/
├── __init__.py        # Public API (convert, get_registry, models)
├── __main__.py        # python -m docparser 지원
├── cli.py             # CLI (argparse, registry 기반 자동 라우팅)
├── models.py          # Document model (Paragraph, Table, Image, ListItem, ...)
├── protocols.py       # Parser / Writer Protocol (구조적 서브타이핑)
├── registry.py        # FormatRegistry (확장자→파서, 포맷명→Writer 매핑)
├── parsers/
│   ├── hwp.py         # HWP v5 binary parser (olefile)
│   └── hwpx.py        # HWPX parser (zipfile + xml.etree)
└── writers/
    └── markdown.py    # Markdown writer
```

### Key modules

- **`protocols.py`** — `Parser` and `Writer` Protocol classes. No inheritance needed; just match the static method signatures (`extensions()`, `parse()` / `format_name()`, `write()`).
- **`registry.py`** — `FormatRegistry` maps file extensions to parsers and format names to writers. Singleton via `get_registry()`. Auto-registers built-in parsers/writers on first access.
- **`models.py`** — Shared document model. `Document` contains `list[DocumentElement]` and `Metadata`. Element types: `Paragraph`, `Table`, `Image`, `ListItem`, `Link`, `HorizontalRule`.
- **`parsers/hwp.py`** — HWP v5 binary parser using `olefile`. Uses `RecordCursor` for record traversal, `scan_para_chars()` for unified character scanning, and 3-phase table parsing (`_find_table_ctrl` → `_read_table_dimensions` → `_collect_table_cells`).
- **`parsers/hwpx.py`** — HWPX (ZIP+XML) parser using stdlib `xml.etree`. Namespace-agnostic with `_strip_ns()` / `_children()` utilities.
- **`writers/markdown.py`** — Converts `Document` to Markdown. Tables become pipe-format with `<br>` for multi-line cells.

### Library usage (from external projects)

```python
# Direct import
from docparser.parsers.hwp import HwpParser
from docparser.writers.markdown import MarkdownWriter
doc = HwpParser.parse("document.hwp")
md = MarkdownWriter.write(doc)

# Registry auto-routing
from docparser import get_registry
doc = get_registry().parse("document.hwp")
md = get_registry().write(doc, "markdown")

# One-line conversion
from docparser import convert
convert("document.hwp", "output.md")
```

## HWP Binary Format Notes

- Records have a 4-byte header: tag (10 bits), level (10 bits), size (12 bits). If size == 0xFFF (`EXTENDED_SIZE_SENTINEL`), next 4 bytes hold actual size.
- Key tags: `HWPTAG_PARA_HEADER`=66, `HWPTAG_PARA_TEXT`=67, `HWPTAG_CTRL_HEADER`=71, `HWPTAG_LIST_HEADER`=72, `HWPTAG_TABLE`=77.
- PARA_TEXT contains UTF-16LE text. Extended control chars (`EXTENDED_CTRL_CHARS`: codes 0-8, 11-12, 14-23) occupy 16 bytes; inline chars (`CHAR_TAB`=9, `CHAR_LINE_BREAK`=10, `CHAR_PARAGRAPH_END`=13) occupy 2 bytes.
- Table parsing: detect `CHAR_TABLE_OBJECT` (11) → find CTRL_HEADER with `CTRL_TABLE_ID` → read TABLE record for dimensions → collect cell text from LIST_HEADER/PARA_TEXT.
- 1×1 tables are treated as text wrappers and unwrapped to plain paragraphs.

## Adding New Formats

See `docs/adding-formats.md`. In short: create a parser/writer class matching the Protocol, register it in `registry.py:_auto_register()`.

## Dependencies

Core: `olefile` (BSD) only. `lxml` removed (hwpx.py uses stdlib `xml.etree`). Optional: `pymupdf` (PDF), `pillow`+`pytesseract` (OCR).
