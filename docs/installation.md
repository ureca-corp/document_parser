# 설치

## 기본 설치

[uv](https://docs.astral.sh/uv/)를 사용해서 설치할 수 있어요.

```bash
uv add ureca_document_parser
```

pip를 사용한다면:

```bash
pip install ureca_document_parser
```

이렇게 하면 HWP와 HWPX 파일을 Markdown으로 변환하는 기본 기능을 사용할 수 있어요.

## 선택적 의존성

필요한 기능에 따라 추가 의존성을 설치할 수 있어요.

### LangChain 청크 분할

[langchain-text-splitters](https://python.langchain.com/docs/how_to/recursive_text_splitter/)를 사용해서 문서를 RAG용 청크로 분할해요.

```bash
uv add "ureca_document_parser[langchain]"
```

이후 `convert_to_chunks()` 함수를 사용할 수 있어요. 자세한 내용은 [LangChain 연동 가이드](guides/langchain.md)를 참고하세요.

### PDF 파싱

!!! warning "준비 중"
    PDF 파싱 기능은 아직 개발 중이에요.

[PyMuPDF](https://pymupdf.readthedocs.io/)를 사용해서 PDF 파일을 파싱해요.

```bash
uv add "ureca_document_parser[pdf]"
```

### OCR (이미지 텍스트 추출)

!!! warning "준비 중"
    OCR 기능은 아직 개발 중이에요.

[Pillow](https://pillow.readthedocs.io/) + [pytesseract](https://github.com/madmaze/pytesseract)를 사용해서 이미지에서 텍스트를 추출해요.

```bash
uv add "ureca_document_parser[ocr]"
```

### 모든 기능 설치

```bash
uv add "ureca_document_parser[all]"
```

## 개발 환경 설정

라이브러리 자체를 수정하거나 기여하고 싶다면 저장소를 클론하고 개발 의존성을 설치하세요.

```bash
git clone https://github.com/ureca-corp/document_parser.git
cd document_parser
uv sync --extra dev
```

테스트 실행:

```bash
uv run pytest tests/ -v
```

자세한 내용은 [포맷 확장 가이드](reference/extending.md)를 참고하세요.

## 다음 단계

- [CLI 사용법](guides/cli.md)
- [Python API 사용법](guides/python-api.md)
