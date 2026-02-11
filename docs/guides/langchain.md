# LangChain 연동

`ureca_document_parser`는 [LangChain](https://python.langchain.com/)과 완벽하게 통합돼서 RAG(Retrieval-Augmented Generation) 파이프라인을 쉽게 구축할 수 있어요.

## 사전 준비

LangChain 기능을 사용하려면 추가 의존성이 필요해요.

```bash
uv add "ureca_document_parser[langchain]"
```

이렇게 하면 [langchain-text-splitters](https://python.langchain.com/docs/how_to/recursive_text_splitter/)와 [langchain-core](https://python.langchain.com/docs/versions/v0_3/)가 함께 설치돼요.

## LangChain 청크로 변환하기

### 기본 사용법

`convert()` 함수에 `chunks=True`를 지정하면 HWP/HWPX 파일을 파싱하고, 텍스트를 청크로 분할해서 `LangChain Document` 리스트를 반환해요.

```python
from ureca_document_parser import convert

chunks = convert("보고서.hwp", chunks=True, chunk_size=1000, chunk_overlap=200)

for chunk in chunks:
    print(chunk.page_content[:100])  # 청크 내용 일부
    print(chunk.metadata)             # {'source': '보고서.hwp', 'format': 'hwp'}
    print("---")
```

### 매개변수

- `input_path` (필수): 변환할 HWP 또는 HWPX 파일 경로
- `chunks` (필수): `True`로 설정
- `chunk_size` (선택, 기본값 1000): 각 청크의 최대 문자 수
- `chunk_overlap` (선택, 기본값 200): 인접 청크 간 중복 문자 수

### 청킹 매개변수 가이드

| 매개변수 | 기본값 | 권장값 | 설명 |
|---------|--------|--------|------|
| `chunk_size` | 1000 | 500~2000 | 각 청크의 최대 문자 수예요. 임베딩 모델의 최대 토큰 수를 고려해서 설정하세요. |
| `chunk_overlap` | 200 | chunk_size의 10~20% | 인접 청크 간 중복 문자 수예요. 문맥 연속성을 유지해서 검색 품질을 높여요. |

!!! tip "매개변수 선택 가이드"
    **chunk_size 선택하기:**

    - **짧은 청크 (500~800)**: 정확한 정보 검색에 유리해요. 특정 수치나 용어를 찾을 때 적합해요.
    - **중간 청크 (1000~1500)**: 범용적으로 사용하기 좋아요. 문맥과 정확성의 균형이 적당해요.
    - **긴 청크 (1500~2000)**: 긴 문맥이 필요한 요약이나 분석에 적합해요. 단, 임베딩 모델의 토큰 제한을 확인하세요.

    **chunk_overlap 선택하기:**

    - **작은 중복 (10%)**: 처리 속도와 저장 공간이 중요할 때 사용해요.
    - **중간 중복 (15~20%)**: 일반적인 RAG 파이프라인에 적합해요. 문장이나 단락이 청크 경계에서 잘리는 것을 방지해요.
    - **큰 중복 (20~30%)**: 매우 긴밀한 문맥 연결이 필요할 때 사용하지만, 중복 정보가 많아질 수 있어요.

    **사용 예시:**

    ```python
    # 짧은 FAQ 문서: 정확한 답변 검색
    chunks = convert("FAQ.hwp", chunks=True, chunk_size=600, chunk_overlap=60)

    # 긴 보고서: 문맥 기반 질의응답
    chunks = convert("보고서.hwp", chunks=True, chunk_size=1500, chunk_overlap=300)

    # 기술 문서: 균형잡힌 설정
    chunks = convert("매뉴얼.hwp", chunks=True, chunk_size=1000, chunk_overlap=200)
    ```

## 실전 예시

### 벡터 스토어에 저장하기 (Chroma)

```python
from ureca_document_parser import convert
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma

# 문서 청크 생성
chunks = convert("보고서.hwp", chunks=True, chunk_size=1000, chunk_overlap=200)

# 임베딩 생성 및 벡터 스토어에 저장
embeddings = OpenAIEmbeddings()
vectorstore = Chroma.from_documents(documents=chunks, embedding=embeddings)

# 검색
query = "프로젝트 일정은?"
results = vectorstore.similarity_search(query, k=3)

for result in results:
    print(result.page_content)
    print("---")
```

### 여러 파일 일괄 처리

```python
from pathlib import Path
from ureca_document_parser import convert
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma

# 모든 HWP/HWPX 파일에서 청크 생성
all_chunks = []
for file in Path("documents").glob("*.hwp"):
    chunks = convert(file, chunks=True, chunk_size=1000, chunk_overlap=200)
    all_chunks.extend(chunks)
    print(f"✓ {file.name}: {len(chunks)}개 청크")

print(f"\n총 {len(all_chunks)}개 청크 생성")

# 벡터 스토어에 한 번에 저장
embeddings = OpenAIEmbeddings()
vectorstore = Chroma.from_documents(documents=all_chunks, embedding=embeddings)
```

### RAG 체인 구축하기

```python
from ureca_document_parser import convert
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_chroma import Chroma
from langchain.chains import RetrievalQA

# 1. 문서 로드 및 청크 생성
chunks = convert("보고서.hwp", chunks=True)

# 2. 벡터 스토어 생성
embeddings = OpenAIEmbeddings()
vectorstore = Chroma.from_documents(documents=chunks, embedding=embeddings)

# 3. RAG 체인 구축
llm = ChatOpenAI(model="gpt-4")
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=vectorstore.as_retriever(search_kwargs={"k": 3}),
)

# 4. 질문하기
response = qa_chain.invoke("프로젝트의 주요 목표는 무엇인가요?")
print(response["result"])
```

### 메타데이터 활용하기

청크의 메타데이터를 사용해서 필터링하거나 추적할 수 있어요.

```python
from ureca_document_parser import convert

chunks = convert("보고서.hwp", chunks=True)

for chunk in chunks:
    print(f"출처: {chunk.metadata['source']}")
    print(f"포맷: {chunk.metadata['format']}")
    print(f"내용: {chunk.page_content[:100]}...")
    print("---")
```

여러 파일을 처리할 때 출처를 추적하는 예시:

```python
from pathlib import Path
from ureca_document_parser import convert
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma

all_chunks = []

for file in Path("documents").glob("*.hwp"):
    chunks = convert(file, chunks=True)
    all_chunks.extend(chunks)

# 벡터 스토어에 저장
embeddings = OpenAIEmbeddings()
vectorstore = Chroma.from_documents(documents=all_chunks, embedding=embeddings)

# 검색 후 출처 확인
results = vectorstore.similarity_search("예산 계획", k=3)
for result in results:
    print(f"출처: {result.metadata['source']}")
    print(f"내용: {result.page_content[:100]}...")
    print("---")
```

## 고급: 직접 청크 분할하기

더 세밀한 제어가 필요하다면 `RecursiveCharacterTextSplitter`를 직접 사용할 수 있어요.

```python
from ureca_document_parser import convert
from langchain_text_splitters import RecursiveCharacterTextSplitter

# 1. 문서를 Markdown 문자열로 변환
markdown_text = convert("보고서.hwp")  # output_path 없이 호출하면 문자열 반환

# 2. 커스텀 구분자로 청크 분할
splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    separators=["\n## ", "\n### ", "\n\n", "\n", " ", ""],  # 헤딩 우선 분할
    length_function=len,
)

chunks = splitter.create_documents(
    [markdown_text],
    metadatas=[{"source": "보고서.hwp", "format": "hwp", "custom_field": "value"}],
)
```

## 다른 벡터 스토어 사용하기

### Pinecone

```python
from ureca_document_parser import convert
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore

chunks = convert("보고서.hwp", chunks=True)

embeddings = OpenAIEmbeddings()
vectorstore = PineconeVectorStore.from_documents(
    documents=chunks,
    embedding=embeddings,
    index_name="hwp-documents",
)
```

### FAISS

```python
from ureca_document_parser import convert
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS

chunks = convert("보고서.hwp", chunks=True)

embeddings = OpenAIEmbeddings()
vectorstore = FAISS.from_documents(chunks, embeddings)

# 로컬에 저장
vectorstore.save_local("faiss_index")

# 나중에 로드
vectorstore = FAISS.load_local("faiss_index", embeddings)
```

## 성능 최적화

### 병렬 처리

여러 파일을 빠르게 처리하려면 병렬 처리를 사용하세요.

```python
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from ureca_document_parser import convert

def process_file(file_path):
    chunks = convert(file_path, chunks=True)
    return chunks

files = list(Path("documents").glob("*.hwp"))

with ThreadPoolExecutor(max_workers=4) as executor:
    results = executor.map(process_file, files)

all_chunks = [chunk for chunks in results for chunk in chunks]
print(f"총 {len(all_chunks)}개 청크 생성")
```

## 다음 단계

- [고급 사용법](advanced.md) — Document 모델 직접 다루기
- [Python API 가이드](python-api.md) — 더 많은 사용 예시
- [API 레퍼런스](../api-reference.md) — 전체 API 문서
