# RAG Pipeline 구현

`new_py` 폴더의 코드를 활용하여 모듈화된 RAG 파이프라인을 구현했습니다.

## 📁 프로젝트 구조

```
src/
├── data_processing/
│   ├── data_processor.py         # 데이터 전처리 및 청킹
│   └── vector_store_manager.py   # 벡터스토어 관리
├── retrieval/
│   └── rag_handler.py            # RAG 검색 처리
├── generation/
│   └── llm_generator.py          # LLM 응답 생성
└── run_rag_pipeline.py           # 메인 실행 스크립트
```

## 🚀 사용 방법

### 1. 환경 설정

`.env` 파일에 OpenAI API 키를 설정하세요:

```bash
OPENAI_API_KEY=your-api-key-here
```

### 2. 패키지 설치

```bash
pip install -r requirements.txt
```

### 3. RAG 파이프라인 실행

```bash
cd src
python run_rag_pipeline.py
```

메뉴에서 선택:
- **1. 벡터스토어 생성**: 처음 실행 시 데이터를 벡터화하여 저장
- **2. RAG 쿼리 실행**: 질문을 입력하여 답변 받기
- **3. 테스트 실행**: 미리 준비된 테스트 쿼리 실행
- **4. 종료**

## 📝 주요 기능

### 1. 데이터 전처리 (`data_processor.py`)

- **의학 데이터 로드**: 말뭉치 데이터 (medical_data)
- **QA 데이터 로드**: 질의응답 데이터 (qa_data)
- **적응형 청킹**: 데이터 타입에 따라 다른 청킹 전략 적용
  - medical_data: chunk_size=500, overlap=100
  - qa_data: chunk_size=800, overlap=50

### 2. 벡터스토어 관리 (`vector_store_manager.py`)

- **OpenAI Embeddings**: text-embedding-3-small 모델 사용
- **Chroma DB**: 로컬 벡터 데이터베이스
- **배치 처리**: API 제한을 고려한 배치 처리
- **검색 기능**: similarity search, retriever 제공

### 3. RAG 검색 (`rag_handler.py`)

- **문서 검색**: 벡터 유사도 기반 검색
- **문서 포맷팅**: 출처 정보를 포함한 구조화된 포맷
- **폴백 메커니즘**: RAG 실패 시 웹 검색으로 전환 (CRAG)

### 4. LLM 생성 (`llm_generator.py`)

- **쿼리 재작성**: 검색 최적화를 위한 쿼리 변환
- **프롬프트 엔지니어링**: 반려견 건강 상담에 특화된 프롬프트
- **응답 생성**: GPT-4o-mini 모델 사용
- **출처 명시**: 답변에 사용된 문서 출처 포함

## 🔧 핵심 컴포넌트

### VectorStoreManager

```python
from data_processing.vector_store_manager import VectorStoreManager

# 벡터스토어 생성
manager = VectorStoreManager()
manager.create_vectorstore(documents)

# 검색
docs = manager.search_similar_chunks("강아지 구토", top_k=5)
```

### RAG Handler

```python
from retrieval.rag_handler import perform_rag_search, get_retriever

# 문서 검색
context = perform_rag_search("강아지 피부염", k=5)

# 리트리버 사용
retriever = get_retriever(search_type="similarity", k=5)
```

### LLM Generator

```python
from generation.llm_generator import generate_response, rewrite_query

# 쿼리 재작성
transformed = rewrite_query("우리 강아지가 토해요")

# 응답 생성
response = generate_response(query, context)
```

## 📊 데이터 처리 과정

1. **데이터 로드** → JSON 파일에서 문서 추출
2. **메타데이터 추가** → source_type, department 등
3. **청킹** → 데이터 타입별 최적 크기로 분할
4. **임베딩** → OpenAI embeddings로 벡터화
5. **저장** → Chroma DB에 인덱싱

## 🎯 프롬프트 전략

### 할루시네이션 방지
- 문맥에 없는 정보는 생성하지 않음
- 출처 명시 강제
- "문서에 정보가 없습니다" 명시적 표현

### 응답 구조
```
- 상태 요약
- 가능한 원인
- 집에서 관리 방법
- 병원 방문 시기
- 출처 (참고한 모든 문서)
```

## 🔄 워크플로우

```
사용자 질문
    ↓
쿼리 재작성 (선택적)
    ↓
벡터 검색 (top-k=5)
    ↓
문서 포맷팅
    ↓
LLM 응답 생성
    ↓
최종 답변 (출처 포함)
```

## 📦 new_py 폴더 코드 활용

- `data preprocessing.py` → `data_processor.py`
  - 의학 데이터 & QA 데이터 로딩 로직
  - 적응형 청킹 전략
  
- `vectorstore.py` → `vector_store_manager.py`
  - 배치 처리 로직
  - Chroma DB 연동
  
- `prompt.py` → `llm_generator.py` & `rag_handler.py`
  - RAG 프롬프트
  - 쿼리 재작성 프롬프트
  - 문서 포맷팅 함수

## ⚙️ 설정 옵션

### 벡터스토어 설정
```python
VectorStoreManager(
    collection_name="pet_health_qa_system",
    persist_directory="./chroma_db",
    embedding_model="text-embedding-3-small"
)
```

### 검색 설정
```python
perform_rag_search(query, k=5)  # 검색할 문서 개수
```

### LLM 설정
```python
generate_response(
    query, 
    context, 
    model="gpt-4o-mini",
    temperature=0
)
```

## 🐛 문제 해결

### 벡터스토어가 없다는 오류
→ 먼저 "1. 벡터스토어 생성" 메뉴를 실행하세요

### API 키 오류
→ `.env` 파일에 `OPENAI_API_KEY`가 설정되어 있는지 확인하세요

### 경로 오류
→ `run_rag_pipeline.py`의 `base_path`를 실제 데이터 경로에 맞게 수정하세요

## 📈 성능 최적화

- **배치 처리**: 100개 문서씩 배치 처리하여 API 제한 회피
- **에러 핸들링**: 배치 실패 시 더 작은 배치로 재시도
- **속도 제어**: API 호출 간 1초 대기

## 🎓 참고 자료

- LangChain: https://python.langchain.com/
- Chroma DB: https://docs.trychroma.com/
- OpenAI Embeddings: https://platform.openai.com/docs/guides/embeddings
