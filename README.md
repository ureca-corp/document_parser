# ureca_document_parser

[![PyPI version](https://badge.fury.io/py/ureca-document-parser.svg)](https://pypi.org/project/ureca-document-parser/)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

한국어 워드프로세서 문서(HWP/HWPX)를 Markdown으로 변환하는 파이썬 라이브러리예요. LangChain과 완벽하게 통합되어 RAG 파이프라인 구축에 최적화되어 있어요.

## 주요 기능

- ✅ **HWP/HWPX 지원** — 아래한글 바이너리(HWP) 및 XML(HWPX) 포맷 모두 파싱
- 📝 **Markdown 변환** — 문단, 표, 리스트, 헤딩을 Markdown으로 변환
- 🔗 **LangChain 통합** — RAG 파이프라인을 위한 문서 청킹 기능 내장
- 🎯 **간단한 API** — 한 줄로 변환하는 직관적인 인터페이스
- 🛠️ **CLI 도구** — 커맨드라인에서 바로 사용 가능
- 🔧 **확장 가능** — 새로운 포맷 추가가 쉬운 클린 아키텍처

## 설치

### 기본 설치 (HWP/HWPX만)

```bash
uv add ureca_document_parser
```

또는 pip 사용:

```bash
pip install ureca_document_parser
```

### LangChain 통합 포함

```bash
uv add "ureca_document_parser[langchain]"
```

## 빠른 시작

### Python API

```python
from ureca_document_parser import convert

# 파일로 저장
convert("보고서.hwp", "보고서.md")

# 문자열로 반환
markdown = convert("보고서.hwp")
print(markdown)

# LangChain 청크로 반환 (RAG용)
chunks = convert("보고서.hwp", chunks=True, chunk_size=1000, chunk_overlap=200)
for chunk in chunks:
    print(chunk.page_content)
```

### CLI

```bash
# 파일 변환
uv run ureca_document_parser 보고서.hwp -o 보고서.md

# 표준 출력으로
uv run ureca_document_parser 보고서.hwp

# 여러 파일 일괄 변환
for file in *.hwp; do
    uv run ureca_document_parser "$file" -o "${file%.hwp}.md"
done
```

## LangChain과 함께 사용하기

```python
from ureca_document_parser import convert
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma

# 문서를 청크로 변환
chunks = convert("보고서.hwp", chunks=True)

# 벡터 스토어에 저장
embeddings = OpenAIEmbeddings()
vectorstore = Chroma.from_documents(documents=chunks, embedding=embeddings)

# 검색
results = vectorstore.similarity_search("프로젝트 일정은?", k=3)
```

## 지원 포맷

| 포맷 | 확장자 | 설명 |
|------|--------|------|
| HWP | `.hwp` | 아래한글 바이너리 포맷 (v5.0+) |
| HWPX | `.hwpx` | 아래한글 XML 포맷 (2014+) |

## 문서

자세한 사용법과 API 문서는 [공식 문서](https://ureca-corp.github.io/document_parser/)를 참고하세요:

- [시작하기](https://ureca-corp.github.io/document_parser/getting-started/) — 설치 및 기본 사용법
- [Python API 가이드](https://ureca-corp.github.io/document_parser/guides/python-api/) — 다양한 사용 예시
- [LangChain 연동](https://ureca-corp.github.io/document_parser/guides/langchain/) — RAG 파이프라인 구축
- [API 레퍼런스](https://ureca-corp.github.io/document_parser/api-reference/) — 전체 API 문서

## 제한사항

현재 버전에서는 다음 기능을 지원하지 않아요:

- 이미지 추출 (대체 텍스트만 표시)
- 도형 및 차트
- 머리글/바닥글
- 각주/미주
- 복잡한 표 병합 구조

## 개발

```bash
# 개발 환경 설정
git clone https://github.com/ureca-corp/document_parser.git
cd document_parser
uv sync --extra dev

# 테스트 실행
uv run pytest tests/ -v

# 문서 미리보기
uv sync --extra docs
uv run mkdocs serve
```

## 라이선스

MIT License - 자세한 내용은 [LICENSE](LICENSE) 파일을 참고하세요.

## 기여

기여는 언제나 환영이에요! [이슈](https://github.com/ureca-corp/document_parser/issues)를 통해 버그 리포트나 기능 제안을 해주세요.

## 링크

- 📚 [문서](https://ureca-corp.github.io/document_parser/)
- 📦 [PyPI](https://pypi.org/project/ureca-document-parser/)
- 🐛 [이슈 트래커](https://github.com/ureca-corp/document_parser/issues)
- 💻 [소스 코드](https://github.com/ureca-corp/document_parser)
