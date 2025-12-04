# 🏗️ 반려동물 의료 RAG 시스템 - 상세 아키텍처

## 목차

1. [시스템 개요](#시스템-개요)
2. [모듈별 아키텍처](#모듈별-아키텍처)
3. [데이터 흐름](#데이터-흐름)
4. [CRAG 파이프라인 상세](#crag-파이프라인-상세)
5. [확장 포인트](#확장-포인트)
6. [성능 고려사항](#성능-고려사항)

---

## 시스템 개요

### 핵심 설계 원칙

1. **모듈식 (Modular)**: 각 컴포넌트가 독립적
2. **확장성 (Extensible)**: 새로운 기능 추가 용이
3. **테스트 가능성 (Testable)**: 단위 테스트 지원
4. **명확한 인터페이스 (Clear Interface)**: 타입 정의 및 docstring

### 전체 워크플로우

```
사용자 입력 (자연어 질문)
    ↓
[QueryOrchestrator]
    ├─→ [QuestionClassifier] 의도 분류
    ├─→ 의도별 처리 라우팅
    │   ├─→ medical → [LangGraphRAGPipeline]
    │   ├─→ hospital → [HospitalMapper]
    │   ├─→ general → [GeneralWebSearcher]
    │   └─→ unknown → [Fallback]
    └─→ 최종 응답 생성
    ↓
사용자 인터페이스
```

---

## 모듈별 아키텍처

### 1. Classifier Module (`src/classifier/`)

**목적**: 사용자 질문을 4가지 카테고리로 분류

**구성**:
- `question_classifier.py`: 핵심 분류 로직

**현재 구현**:
- Rule-based 키워드 매칭
- 4가지 의도: medical, hospital, general, unknown

**확장 방향**:

```python
# 단계 1: 현재 (Rule-based)
classifier = QuestionClassifier()
result = classifier.classify("반려견 피부염이...")
# intent: "medical" (신뢰도 95%)

# 단계 2: 향후 (LLM-based)
# OpenAI API를 사용한 더 정교한 분류
result = classifier.classify_with_llm("반려견 피부염이...")
# intent: "medical" (신뢰도 99%)
```

**API**:
```python
class QuestionClassifier:
    def classify(query: str) -> ClassificationResult
    def classify_with_llm(query: str) -> ClassificationResult
    def add_custom_keywords(category: str, keywords: list[str])
```

---

### 2. Retriever Module (`src/retriever/`)

**목적**: 벡터 검색을 통한 의료 문서 검색

**구성**:
- `vector_store_retriever.py`: 벡터 검색 인터페이스

**현재 구현**:
- Mock 데이터 반환 (테스트용)
- ChromaDB 통합 준비

**확장 방향**:

```python
# 단계 1: 현재 (Mock)
retriever = VectorStoreRetriever()
results = retriever.search("반려견 피부염")
# Mock 문서 반환

# 단계 2: ChromaDB 연동
# OpenAI Embedding API를 사용한 실제 벡터 검색
results = retriever.search("반려견 피부염", top_k=5)
# ChromaDB에서 검색된 문서 반환

# 단계 3: Hybrid 검색
# 벡터 검색 + BM25 키워드 검색
results = retriever.search_hybrid("반려견 피부염")
```

**데이터 모델**:
```python
class Document(BaseModel):
    id: str
    content: str
    metadata: Dict[str, Any]
    score: Optional[float]
    source: str

class DocumentBatch(BaseModel):
    documents: List[Document]
    total_count: int
```

**API**:
```python
class VectorStoreRetriever:
    def search(query: str, top_k: int) -> DocumentBatch
    def search_with_filter(query: str, filters: dict, top_k: int) -> DocumentBatch
    def add_documents(documents: List[Document]) -> bool
    def delete_documents(document_ids: List[str]) -> bool
    def health_check() -> bool
```

---

### 3. Web Search Module (`src/web/`)

**목적**: 벡터 검색 실패 시 웹 검색 폴백

**구성**:
- `hospital_web_searcher.py`: 병원 정보 검색
- `general_web_searcher.py`: 일반 정보 검색

**현재 구현**:
- Mock 검색 결과 반환

**확장 방향**:

```python
# 단계 1: 현재 (Mock)
searcher = GeneralWebSearcher()
results = searcher.search("반려견 피부염")
# Mock 결과 반환

# 단계 2: Google Custom Search API 연동
results = searcher.search("반려견 피부염")
# Google 검색 결과 반환

# 단계 3: 다중 소스 통합
results = searcher.search("반려견 피부염")
# Google + Naver + Scholar 결과 통합
```

**API**:
```python
class GeneralWebSearcher:
    def search(query: str, max_results: int) -> List[Dict]
    def search_academic(query: str) -> List[Dict]
    def search_news(query: str) -> List[Dict]
    def get_page_content(url: str) -> str
    def summarize_results(results: List[Dict]) -> Dict

class HospitalWebSearcher:
    def search(query: str) -> List[Dict]
    def search_by_location(region: str, district: str) -> List[Dict]
    def search_by_coordinates(lat: float, lon: float, radius_km: float) -> List[Dict]
    def get_hospital_details(hospital_name: str) -> Dict
```

---

### 4. Mapping Module (`src/mapping/`)

**목적**: 지역 정보 추출 및 병원 위치 매핑

**구성**:
- `hospital_mapper.py`: 위치 매핑 로직

**현재 구현**:
- 정규표현식 기반 지역 추출
- Mock 좌표 및 병원 정보 반환

**확장 방향**:

```python
# 단계 1: 현재 (Regex-based)
mapper = HospitalMapper()
result = mapper.extract_and_search("강남역 근처 동물병원")
# {"region": "강남", "hospitals": [...]}

# 단계 2: NER + 카카오맵 API
# 실제 좌표 조회 및 거리 계산
result = mapper.extract_and_search("강남역 근처 동물병원")
# {"coordinates": {lat, lon}, "hospitals": [...with distance]}

# 단계 3: 고급 위치 이해
# "역 근처", "거리상 5km 이내" 등 복잡한 조건 처리
```

**API**:
```python
class HospitalMapper:
    def extract_and_search(query: str) -> Dict[str, Any]
    def extract_location(text: str) -> Dict[str, Optional[str]]
    def get_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float
```

---

### 5. RAG Pipeline Module (`src/rag/`)

**목적**: CRAG (Corrective RAG) 파이프라인 구현

**구성**:
- `langgraph_crag_pipeline.py`: 메인 파이프라인 클래스
- `graph_builder.py`: 그래프 구성
- `nodes/`: 개별 노드 구현
  - `retrieval_node.py`: 벡터 검색
  - `relevance_node.py`: 관련성 평가
  - `web_search_node.py`: 웹 검색 폴백
  - `generation_node.py`: 답변 생성

**CRAG 파이프라인 상세**:

```
INPUT: 사용자 질문
  ↓
[Retrieval Node]
  - 벡터 검색 수행
  - 상위 top_k 문서 반환
  - 실패 → 빈 리스트 반환
  ↓ documents
[Relevance Node]
  - 문서 점수 > threshold 확인
  - 관련 문서 필터링
  - needs_web_search 결정
  ↓
  ├─→ [관련 문서 있음] → needs_web_search = False
  │
  └─→ [관련 문서 없음] → needs_web_search = True
       ↓
      [Web Search Node]
       - HospitalWebSearcher 또는 GeneralWebSearcher 호출
       - 검색 결과를 Document로 변환
       - documents에 추가
  ↓
[Generation Node]
  - 모든 documents를 기반으로 답변 생성
  - LLM 호출 또는 기본 템플릿 사용
  ↓
OUTPUT: RAGResponse
```

**상태 관리**:
```python
state = {
    "query": str,                           # 원본 질문
    "intent": str,                          # 분류된 의도
    "documents": List[Document],            # 검색된 문서
    "relevant_documents": List[Document],   # 관련성 있는 문서
    "web_search_results": List[Dict],       # 웹 검색 결과
    "answer": str,                          # 생성된 답변
    "retrieval_performed": bool,
    "web_search_performed": bool,
    "generation_performed": bool,
}
```

**API**:
```python
class LangGraphRAGPipeline:
    def invoke(query: str, intent: str = "medical") -> RAGResponse
    def invoke_batch(queries: list[str], intent: str) -> list[RAGResponse]
    def get_graph_config() -> Dict[str, Any]
    def add_custom_node(name: str, function: callable, ...) 
    def run_with_streaming(query: str, intent: str)
    def health_check() -> Dict[str, Any]
```

---

### 6. Orchestrator Module (`src/orchestrator/`)

**목적**: 전체 시스템 조율 및 라우팅

**구성**:
- `query_orchestrator.py`: 오케스트레이션 로직

**워크플로우**:

```python
def process(query: str) -> Dict[str, Any]:
    # 1. 의도 분류
    classification = classifier.classify(query)
    intent = classification.intent
    
    # 2. 의도별 라우팅
    if intent == "medical":
        # RAG 파이프라인 사용
        response = rag_pipeline.invoke(query)
    elif intent == "hospital":
        # 병원 매핑 사용
        response = hospital_mapper.extract_and_search(query)
    elif intent == "general":
        # 웹 검색 사용
        response = general_searcher.search(query)
    else:
        # 폴백: 웹 검색
        response = general_searcher.search(query)
    
    return {
        "type": response_type,
        "data": response
    }
```

**API**:
```python
class QueryOrchestrator:
    def process(query: str) -> Dict[str, Any]
    def get_statistics() -> Dict[str, Any]
```

---

## 데이터 흐름

### 전체 데이터 흐름도

```
사용자 입력 (text)
    ↓
QueryOrchestrator.process()
    ↓
├─→ QuestionClassifier
│       ↓
│   ClassificationResult
│   (intent, confidence, query)
│
├─→ 의도별 처리
│   ├─→ medical intent
│   │   ├─→ LangGraphRAGPipeline
│   │   │   ├─→ VectorStoreRetriever.search()
│   │   │   │   ↓
│   │   │   │   DocumentBatch
│   │   │   │
│   │   │   ├─→ Relevance evaluation
│   │   │   │   ↓
│   │   │   │   relevant_documents
│   │   │   │
│   │   │   ├─→ IF no relevant docs
│   │   │   │   ├─→ HospitalWebSearcher.search()
│   │   │   │   │   ↓ web_search_results
│   │   │   │   └─→ convert_web_results_to_documents()
│   │   │   │       ↓ documents
│   │   │   │
│   │   │   └─→ Generation
│   │   │       ↓ answer
│   │   │
│   │   └─→ RAGResponse
│   │
│   ├─→ hospital intent
│   │   ├─→ HospitalMapper
│   │   │   ├─→ extract_location()
│   │   │   ├─→ get_coordinates()
│   │   │   └─→ search_hospitals_nearby()
│   │   │       ↓ hospitals, location
│   │   │
│   │   └─→ HospitalResponse
│   │
│   └─→ general intent
│       ├─→ GeneralWebSearcher.search()
│       │   ↓ results
│       └─→ RAGResponse
│
└─→ 응답 포맷팅 (Streamlit UI)
        ↓
    사용자 표시
```

### 타입 시스템

```
Query
├─ text: str
├─ intent: Optional[str]
├─ metadata: Dict[str, Any]
└─ language: str

ClassificationResult
├─ query: Query
├─ intent: str
├─ confidence: float
└─ details: Dict[str, Any]

Document
├─ id: str
├─ content: str
├─ metadata: Dict[str, Any]
├─ score: Optional[float]
└─ source: str

DocumentBatch
├─ documents: List[Document]
└─ total_count: int

RAGResponse
├─ query: str
├─ answer: str
├─ documents: List[Document]
├─ intent: str
├─ metadata: Dict[str, Any]
├─ model: Optional[str]
└─ execution_time: Optional[float]

HospitalResponse
├─ query: str
├─ hospitals: List[Dict[str, Any]]
├─ location: Dict[str, Any]
└─ metadata: Dict[str, Any]

ErrorResponse
├─ error_code: str
├─ error_message: str
└─ details: Dict[str, Any]
```

---

## CRAG 파이프라인 상세

### 1. Retrieval Node

```python
def retrieval_node(state) -> state:
    """
    벡터 검색 수행
    
    입력:
    - state["query"]: str
    
    출력:
    - state["documents"]: List[Document]
    - state["retrieval_performed"]: bool
    """
    retriever = VectorStoreRetriever()
    results = retriever.search(query, top_k=5)
    return {"documents": results.documents}
```

**실패 시나리오**: 벡터 DB 연결 실패, 검색어 공백 등

### 2. Relevance Node

```python
def relevance_node(state) -> state:
    """
    문서 관련성 평가
    
    입력:
    - state["documents"]: List[Document]
    
    출력:
    - state["relevant_documents"]: List[Document]
    - state["needs_web_search"]: bool
    """
    relevant = [doc for doc in documents if doc.score >= THRESHOLD]
    needs_search = len(relevant) == 0
    return {
        "relevant_documents": relevant,
        "needs_web_search": needs_search
    }
```

**THRESHOLD 설정**: 기본값 0.5 (설정파일에서 조정 가능)

### 3. Web Search Node (Fallback)

```python
def web_search_node(state) -> state:
    """
    웹 검색 폴백
    
    입력:
    - state["query"]: str
    - state["intent"]: str
    - state["needs_web_search"]: bool
    
    출력:
    - state["web_search_results"]: List[Dict]
    - state["documents"]: List[Document] (기존 + 웹 검색)
    """
    if state["needs_web_search"]:
        if state["intent"] == "hospital":
            searcher = HospitalWebSearcher()
        else:
            searcher = GeneralWebSearcher()
        
        results = searcher.search(query)
        docs = convert_web_results_to_documents(results)
        return {
            "web_search_results": results,
            "documents": state["documents"] + docs
        }
```

### 4. Generation Node

```python
def generation_node(state) -> state:
    """
    최종 답변 생성
    
    입력:
    - state["query"]: str
    - state["documents"]: List[Document]
    
    출력:
    - state["answer"]: str
    """
    # 옵션 1: 기본 템플릿
    answer = _generate_answer_from_documents(state["documents"])
    
    # 옵션 2: LLM 기반 (향후)
    # answer = llm.generate(query, documents)
    
    return {"answer": answer}
```

---

## 확장 포인트

### 1. 새로운 노드 추가

```python
# src/rag/nodes/custom_node.py
def custom_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    커스텀 처리 노드
    """
    # 커스텀 로직
    result = process(state)
    state["custom_result"] = result
    return state

# src/rag/graph_builder.py에서 등록
graph_config["nodes"].append({
    "name": "custom",
    "function": custom_node
})
```

### 2. LLM 기반 분류기

```python
# src/classifier/question_classifier.py에 추가
def classify_with_llm(self, question: str) -> ClassificationResult:
    from langchain.llms import ChatOpenAI
    from langchain.prompts import ChatPromptTemplate
    
    llm = ChatOpenAI(model="gpt-4", temperature=0)
    
    prompt = ChatPromptTemplate.from_template(
        "다음 질문을 medical/hospital/general/unknown 중 하나로 분류하세요:\n{question}"
    )
    
    response = (prompt | llm).invoke({"question": question})
    intent = response.content
    
    return ClassificationResult(
        query=Query(text=question),
        intent=intent,
        confidence=0.95
    )
```

### 3. ChromaDB 실제 연동

```python
# src/retriever/chroma_adapter.py (새 파일)
import chromadb
from chromadb.config import Settings

class ChromaDBAdapter:
    def __init__(self, persist_dir: str):
        settings = Settings(
            chroma_db_impl="duckdb+parquet",
            persist_directory=persist_dir,
            anonymized_telemetry=False
        )
        self.client = chromadb.Client(settings)
    
    def search(self, query_embedding, top_k=5):
        # ChromaDB 검색 구현
        pass
```

### 4. 커스텀 임베딩 모델

```python
# src/retriever/embedding_adapter.py
class OllamaEmbedding:
    def __init__(self, model="mistral"):
        self.model = model
    
    def embed(self, text: str) -> List[float]:
        # Ollama 로컬 임베딩 호출
        pass

class HuggingFaceEmbedding:
    def embed(self, text: str) -> List[float]:
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer('all-MiniLM-L6-v2')
        return model.encode(text)
```

---

## 성능 고려사항

### 1. 응답 시간 최적화

| 단계 | 예상 시간 | 최적화 |
|------|-----------|--------|
| 의도 분류 | 10-50ms | 캐싱, 경량 모델 |
| 벡터 검색 | 100-500ms | 인덱싱, 배치 처리 |
| 관련성 평가 | 50-200ms | 병렬 처리 |
| 웹 검색 | 1-5s | 캐싱, 비동기 |
| 답변 생성 | 1-3s | 스트리밍, 캐싱 |
| **전체** | **2-10s** | - |

### 2. 메모리 최적화

```python
# 배치 처리로 메모리 절약
def process_batch(queries: list[str], batch_size=10):
    for i in range(0, len(queries), batch_size):
        batch = queries[i:i+batch_size]
        results = pipeline.invoke_batch(batch)
        yield results
```

### 3. 캐싱 전략

```python
# Redis를 사용한 결과 캐싱
import redis

cache = redis.Redis(host='localhost', port=6379)

@cache_result(ttl=3600)
def classify_query(query: str):
    return classifier.classify(query)
```

### 4. 모니터링

```python
# 성능 메트릭 수집
@timer
def retrieval_node(state):
    # 실행 시간 자동 기록
    pass

# 로깅
logger.info(f"Query processing completed in {elapsed:.2f}s")
logger.info(f"Retrieved {len(documents)} documents")
```

---

## 향후 개선 계획

### Phase 1: 현재 (v0.1)
- ✅ 기본 구조 및 인터페이스
- ✅ Mock 구현 및 테스트
- ✅ Streamlit UI

### Phase 2 (v0.2)
- 📋 LLM 기반 분류기
- 📋 ChromaDB 실제 연동
- 📋 Google/Kakao API 연동

### Phase 3 (v0.3)
- 📋 LLM 기반 답변 생성
- 📋 성능 최적화
- 📋 고급 모니터링

### Phase 4 (v1.0)
- 📋 프로덕션 배포
- 📋 멀티모달 지원
- 📋 고급 분석 대시보드

---

**[README.md](README.md)로 돌아가기**

