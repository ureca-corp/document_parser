# CLAUDE.md

## 프로젝트 개요

`ureca_document_parser` — 한국어 워드프로세서(아래한글) HWP/HWPX 파일을 Markdown 또는 LangChain Document 청크로 변환하는 다중 포맷 문서 파서. PyPI 배포 가능한 패키지로, 클린 아키텍처 기반으로 새 포맷 확장이 용이하다.

## 명령어

```bash
uv sync
uv run ureca_document_parser <file.hwp|file.hwpx> -o <output.md>
uv run ureca_document_parser --list-formats
uv run python -m ureca_document_parser <file.hwp> -o <output.md>
uv run pytest tests/ -v
uv build
```

## 아키텍처

**파이프라인**: 입력 파일 → 포맷 레지스트리 → 파서 → Document 모델 → Writer → 출력 (또는 → TextSplitter → LangChain Documents)

```
src/ureca_document_parser/
├── __init__.py        # 공개 API (convert, convert_to_chunks, get_registry)
├── __main__.py        # python -m ureca_document_parser
├── cli.py             # CLI (argparse, 레지스트리 기반 자동 라우팅)
├── models.py          # Document 모델 (Paragraph, Table, Image, ListItem, ...)
├── protocols.py       # Parser / Writer Protocol (구조적 서브타이핑)
├── registry.py        # FormatRegistry (확장자→파서, 포맷명→Writer 매핑, 스레드 안전 싱글톤)
├── styles.py          # 공유 헤딩 패턴
├── hwp/
│   ├── __init__.py    # HwpParser 및 저수준 타입 re-export
│   ├── parser.py      # HWP v5 바이너리 파서 (olefile) — 오케스트레이션
│   ├── records.py     # 바이너리 레코드 파싱 (Record, RecordCursor, 상수)
│   ├── text.py        # 문자 스캐닝 및 텍스트 추출 (CharInfo, BSTR)
│   └── tables.py      # 3단계 테이블 추출
├── hwpx/
│   ├── __init__.py    # HwpxParser re-export
│   └── parser.py      # HWPX 파서 (zipfile + xml.etree)
└── writers/
    └── markdown.py    # Markdown 작성기
```

### 주요 모듈

- **`protocols.py`** — `Parser` / `Writer` Protocol. 상속 없이 정적 메서드 시그니처만 맞추면 된다.
- **`registry.py`** — `FormatRegistry`가 확장자→파서, 포맷명→Writer를 매핑. `get_registry()`로 스레드 안전 싱글톤 접근.
- **`models.py`** — 공유 문서 모델. `Document` = `list[DocumentElement]` + `Metadata`. 파싱 실패 시 `ParseError`.
- **`hwp/`** — HWP v5 바이너리 파서. `records.py`(레코드 스트림), `text.py`(문자 추출), `tables.py`(테이블 파싱), `parser.py`(오케스트레이션)로 분리.
- **`hwpx/parser.py`** — HWPX (ZIP+XML) 파서. 표준 라이브러리 `xml.etree` 사용.
- **`writers/markdown.py`** — `Document`를 Markdown으로 변환. 연속 `ListItem`을 하나의 블록으로 그룹핑.

### 라이브러리 사용 예시

```python
from ureca_document_parser import convert
convert("보고서.hwp", "보고서.md")

from ureca_document_parser import convert_to_chunks
chunks = convert_to_chunks("보고서.hwp", chunk_size=1000, chunk_overlap=200)
```

## 테스트

```bash
uv run pytest tests/ -v              # 전체 테스트
uv run pytest tests/ --cov           # 커버리지 포함
```

테스트 범위: 모델, 레지스트리, CLI, HWP 파서 (단위 + 통합), HWPX 파서, Markdown 작성기.

## 포맷 확장

`docs/adding-formats.md` 참고. Protocol에 맞는 파서/Writer 클래스를 작성하고 `registry.py:_auto_register()`에 등록한다.

## 의존성

필수: `olefile`. 선택: `langchain-text-splitters`+`langchain-core` (청크 분할), `pymupdf` (PDF), `pillow`+`pytesseract` (OCR). 개발: `pytest`, `pytest-cov`, `mypy`, `ruff`.

## 문서

### 구조

```
docs/
├── index.md              # 홈 — 퀵스타트, 주요 기능
├── getting-started.md    # 설치, CLI, Python API 사용법
├── architecture.md       # 파이프라인, 모듈 의존성, Mermaid 다이어그램
├── adding-formats.md     # 새 파서/Writer 추가 가이드 (기여자용)
└── api/
    ├── index.md          # API 개요 + 최상위 API (mkdocstrings 자동 생성)
    ├── models.md         # Document 모델 (mkdocstrings 자동 생성)
    ├── parsers.md        # HWP/HWPX 파서 (mkdocstrings 자동 생성)
    ├── writers.md        # Markdown Writer (mkdocstrings 자동 생성)
    └── registry.md       # FormatRegistry + Protocol (mkdocstrings 자동 생성)
```

### 작성 규칙

- 말투: es-toolkit 스타일 친근한 존댓말 (`~예요`, `~해요`, `~돼요`)
- 코드와 전용 용어를 제외한 모든 텍스트는 한글로 작성한다.
- 관점: **외부 프로젝트에 설치해서 쓰는 사용자** 기준. 내부 소스코드를 복붙하지 않는다.
- CLI 예제는 반드시 `uv run ureca_document_parser ...` 형태로 작성한다.
- 예제 파일명은 실제 사용 시나리오 기반 (예: `보고서.hwp`, `제안서.hwpx`)
- 외부 의존성을 언급할 때는 **이름에 공식문서 링크**를 걸고, 바로 아래에 `uv add` 코드블록을 넣는다.
- `docs/api/` 하위 파일은 `mkdocstrings`가 docstring에서 자동 생성하므로 설명문만 작성한다.
- `docs/adding-formats.md`만 기여자(contributor) 관점으로 작성한다.
- Mermaid 다이어그램 사용 가능 (mkdocs.yml에 설정 완료)
- MkDocs admonition 사용 가능: `!!! note`, `!!! info`, `!!! warning`

### 빌드 및 미리보기

```bash
uv sync --extra docs                    # 문서 의존성 설치
uv run mkdocs serve                     # http://127.0.0.1:8000 로컬 미리보기
uv run mkdocs build                     # site/ 디렉토리에 정적 파일 빌드
```

### 배포

배포는 자동이다. `main` 브랜치에 push하면 `.github/workflows/docs.yml`이 실행되어 GitHub Pages에 배포된다.

- 워크플로우: `mkdocs gh-deploy --force` → `gh-pages` 브랜치에 push
- Pages 설정: Source = `gh-pages` 브랜치 (GitHub Settings → Pages)
- URL: https://ureca-corp.github.io/document_parser/

수동 배포가 필요한 경우:

```bash
uv run mkdocs gh-deploy --force
```

### 네비게이션

페이지를 추가/삭제하면 `mkdocs.yml`의 `nav:` 섹션을 함께 수정해야 한다.

## CI

GitHub Actions (`.github/workflows/ci.yml`) — `main` 브랜치 push/PR 시 실행. Python 3.12 + 3.13 테스트 매트릭스, ruff 린트/포맷 검사.
