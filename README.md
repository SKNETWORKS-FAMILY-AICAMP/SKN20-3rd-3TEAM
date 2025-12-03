# RAG 시스템 프로젝트

의료 데이터를 기반으로 한 RAG (Retrieval-Augmented Generation) 시스템입니다.

## 프로젝트 구조

```
.
├── src/
│   ├── ingestion.py      # 데이터 ingestion 모듈
│   ├── chunking.py        # 문서 chunking 모듈
│   ├── embeddings.py      # 임베딩 및 벡터 DB 모듈
│   ├── retrieval.py       # 검색 및 reranking 모듈
│   └── pipeline.py        # RAG 파이프라인 모듈
├── main.py                # 메인 실행 파일
├── requirements.txt       # 필요한 패키지 목록
└── README.md             # 프로젝트 설명서
```

## 주요 기능

### 1. 데이터 Ingestion
- `/data/Validation/01.원천데이터` 폴더의 모든 JSON 파일 로드
- JSON 필드 추출 (`disease`, `department`, `title`, `author`, `content` 등)
- LangChain Document 객체로 변환

### 2. Chunking
- 문단 기준 chunking
- 토큰 수: 300-500 tokens
- Overlap: 20-30% (기본값 25%)

### 3. 임베딩 및 벡터 DB
- OpenAI embeddings 또는 HuggingFace embeddings 지원
- Chroma DB 사용
- 저장 스키마: `{id, content, source_path, metadata}`
- 메타데이터에 원천데이터 파일명, JSON 필드 정보 포함

### 4. Retrieval
- Top-K 검색 (기본값: 5-10)
- Cosine similarity 기반 reranking
- 관련성 높은 문서 우선 반환

### 5. LLM 응답 생성
- 검색된 chunk 기반 답변 생성
- Hallucination 방지: 문서에 없는 내용은 "모른다"고 답변
- `rag_pipeline(query: str) → answer: str` 형태

## 설치 방법

1. 필요한 패키지 설치:
```bash
pip install -r requirements.txt
```

2. 환경변수 설정:
`.env` 파일을 생성하고 OpenAI API 키를 설정하세요:
```
OPENAI_API_KEY=your_api_key_here
```

## 사용 방법

### 기본 실행

```bash
python main.py
```

### 코드에서 사용

```python
from main import setup_rag_system

# RAG 시스템 설정
pipeline = setup_rag_system(
    data_dir="data/Validation/01.원천데이터",
    rebuild_vectorstore=True  # 처음 실행 시 True
)

# 질문하기
answer = pipeline.rag_pipeline("벼룩 알러지성 피부염의 증상은 무엇인가요?")
print(answer)

# 출처 정보 포함
result = pipeline.rag_pipeline_with_sources("질문")
print(result['answer'])
print(result['sources'])
```

## 설정 옵션

### 임베딩 모델 선택

`main.py`에서 `EMBEDDING_MODEL_TYPE`을 변경:
- `"openai"`: OpenAI embeddings (기본값, `text-embedding-3-small`)
- `"huggingface"`: HuggingFace embeddings (한국어 모델 사용)

### 벡터스토어 재구축

`main.py`에서 `REBUILD_VECTORSTORE = True`로 설정하면 벡터스토어를 재구축합니다.

### 검색 파라미터 조정

`src/retrieval.py`의 `create_retriever` 함수에서:
- `k`: 초기 검색할 문서 수 (기본값: 10)
- `rerank_k`: Reranking 후 반환할 문서 수 (기본값: 5)

## 모듈 설명

### ingestion.py
- `ingest_data(data_dir)`: 데이터 디렉토리에서 JSON 파일 로드 및 Document 변환

### chunking.py
- `chunk_documents_with_token_range()`: 토큰 범위 지정 chunking

### embeddings.py
- `get_embedding_model()`: 임베딩 모델 생성
- `create_vectorstore()`: 벡터스토어 생성
- `load_vectorstore()`: 기존 벡터스토어 로드

### retrieval.py
- `create_retriever()`: Retriever 생성
- `RerankingRetriever`: Reranking 기능이 있는 Retriever 클래스

### pipeline.py
- `RAGPipeline`: RAG 파이프라인 클래스
- `rag_pipeline()`: 질문에 대한 답변 생성
- `rag_pipeline_with_sources()`: 답변 및 출처 정보 반환

## 주의사항

1. **API 키**: OpenAI API 키가 필요합니다. `.env` 파일에 설정하세요.
2. **데이터 경로**: 기본 데이터 경로는 `data/Validation/01.원천데이터`입니다.
3. **벡터스토어**: 처음 실행 시 벡터스토어 생성에 시간이 걸릴 수 있습니다.
4. **메모리**: 대량의 데이터 처리 시 충분한 메모리가 필요합니다.

## 문제 해결

### Chroma DB 설치 오류
```bash
pip install chromadb --upgrade
```

### 임베딩 모델 오류
- OpenAI API 키 확인
- HuggingFace 모델 사용 시 `sentence-transformers` 설치 확인

### 메모리 부족
- Chunk 크기 줄이기 (`chunking.py`에서 `min_tokens`, `max_tokens` 조정)
- 검색 문서 수 줄이기 (`retrieval.py`에서 `k`, `rerank_k` 조정)

## 라이선스

이 프로젝트는 교육 및 연구 목적으로 제공됩니다.

