# 🏗️ 공통 모듈 가이드

## 📋 개요

프로젝트는 **공통 기준 코드**를 기반으로 각 팀원이 고도화 작업을 진행합니다.

```
┌─────────────────────────────────────┐
│      공통 모듈 (Common Module)      │  ← 모든 팀원이 사용
│   ├─ base.py (인터페이스)           │
│   ├─ config.py (설정)               │
│   ├─ models.py (데이터 모델)        │
│   ├─ pipelines.py (기본 파이프라인) │
│   └─ utils.py (유틸리티)            │
└─────────────────────────────────────┘
         ↓↓↓ 상속/확장 ↓↓↓
┌────────────────────────────────────────────────────┐
│          확장 모듈 (Extensions)                      │
│  ├─ embeddings/ (팀원 A)                           │
│  ├─ retrievers/ (팀원 B)                           │
│  ├─ pipelines/ (팀원 C)                            │
│  └─ modules/ (팀원 D)                              │
└────────────────────────────────────────────────────┘
```

## 🎯 핵심 철학

### 1. **인터페이스 기반 설계**
- 모든 구현은 추상 클래스를 상속
- 구현체 변경 시 나머지 코드에 영향 없음
- 팀원 간 독립적 작업 가능

### 2. **공통 계약**
```python
# 모든 임베딩 모델은 이 인터페이스를 따름
class BaseEmbedding(ABC):
    @abstractmethod
    def embed_text(self, text: str) -> List[float]: pass
    
    @abstractmethod
    def embed_batch(self, texts: List[str]) -> List[List[float]]: pass
```

### 3. **확장성**
- 새로운 구현 추가: `extensions/` 폴더
- 기존 코드 수정 없음
- 플러그인 방식

## 📚 모듈 구조

### common/
```
common/
├── __init__.py              # 패키지 초기화
├── base.py                  # 🔴 핵심: 인터페이스 정의
├── config.py                # 설정 및 상수
├── models.py                # 데이터 구조
├── pipelines.py             # 기본 RAG 파이프라인
├── utils.py                 # 유틸리티 함수
├── extensions/              # 팀원 고도화 영역
│   ├── __init__.py
│   ├── README.md
│   ├── example_implementations.py
│   ├── embeddings/          # 팀원 A 영역
│   ├── retrievers/          # 팀원 B 영역
│   ├── pipelines/           # 팀원 C 영역
│   └── modules/             # 팀원 D 영역
└── COMMON_MODULE_GUIDE.md  # 이 파일
```

## 🚀 빠른 시작

### 1단계: 환경 설정
```bash
# 의존성 설치
pip install -r requirements.txt

# 환경 변수 설정
export OPENAI_API_KEY="sk-..."
export TAVILY_API_KEY="tvly-..."
```

### 2단계: 공통 모듈 import
```python
from common.base import BaseEmbedding, BaseRetriever, BaseRAGPipeline
from common.config import CommonConfig, PipelineConfig
from common.models import Document, QueryRequest, QueryResponse
from common.pipelines import SimpleRAGPipeline
from common.utils import setup_logging, load_json, save_json
```

### 3단계: 기본 구현 사용
```python
# 로깅 설정
logger = setup_logging()

# 설정 로드
config = CommonConfig()

# 간단한 파이프라인 실행
response = pipeline.process("사용자 질문")
print(response['answer'])
print(response['sources'])
```

## 🔧 팀원별 구현 패턴

### 패턴 1: 임베딩 모델 고도화 (팀원 A)
```python
from common.base import BaseEmbedding
from typing import List

class AdvancedEmbedding(BaseEmbedding):
    """더 빠르고 정확한 임베딩 구현"""
    
    def embed_text(self, text: str) -> List[float]:
        # 고도화된 임베딩 로직
        # 예: 텍스트 전처리, 캐싱 등
        pass
    
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        # 배치 처리 최적화
        pass
    
    def get_embedding_dimension(self) -> int:
        return self.dimension
```

### 패턴 2: 검색 알고리즘 개선 (팀원 B)
```python
from common.base import BaseRetriever

class MMRRetriever(BaseRetriever):
    """MMR (Maximum Marginal Relevance) 검색"""
    
    def retrieve(self, query: str, top_k: int = 5, **kwargs):
        # MMR 알고리즘으로 다양성 고려한 검색
        pass
```

### 패턴 3: RAG 파이프라인 고도화 (팀원 C)
```python
from common.pipelines import SimpleRAGPipeline

class CRAGPipeline(SimpleRAGPipeline):
    """CRAG (Corrective RAG) 구현"""
    
    def process(self, query: str, **kwargs):
        # Step 1-3: 기본 파이프라인 실행
        base_response = super().process(query, **kwargs)
        
        # Step 4: 웹 검색 추가 (고도화)
        if not has_relevant_docs:
            web_results = self.web_search.search(query)
            # 웹 검색 결과로 재처리
        
        return enhanced_response
```

### 패턴 4: 도메인 특화 RAG (팀원 D)
```python
from common.pipelines import SimpleRAGPipeline

class MedicalRAG(SimpleRAGPipeline):
    """의료 도메인 특화 RAG"""
    
    def _get_generation_prompt(self, query: str, context: str) -> str:
        # 의료 도메인 특화 프롬프트 템플릿
        return f"""
        당신은 의료 전문가입니다.
        
        <의료 정보>
        {context}
        </의료 정보>
        
        환자 질문: {query}
        
        주의: 의료 정보는 참고만 하고, 항상 의사 진료를 권장하세요.
        """
```

## 📊 데이터 흐름

```
사용자 질문 (QueryRequest)
         ↓
┌─────────────────────┐
│  Retrieve 단계       │  ← 팀원 B 담당 영역
│ (문서 검색)          │     - BaseRetriever 구현
└─────────────────────┘
         ↓
    [검색 결과]
         ↓
┌─────────────────────┐
│  Grade 단계          │  ← 기본 구현 (확장 가능)
│ (관련성 평가)        │
└─────────────────────┘
         ↓
    [관련 문서만]
         ↓
┌─────────────────────┐
│  Generate 단계       │  ← 팀원 D 담당 (도메인)
│ (답변 생성)          │     - 도메인 프롬프트
└─────────────────────┘
         ↓
 응답 (QueryResponse)
```

## 🔌 컴포넌트 연동

### 기본 파이프라인 (공통 기준)
```python
from common.pipelines import SimpleRAGPipeline

pipeline = SimpleRAGPipeline(
    retriever=기본_retriever,
    embedding_model=기본_embedding,
    vector_store=기본_vectorstore,
    llm_client=기본_llm,
)
```

### 고도화 파이프라인 (팀원들의 구현)
```python
from extensions.pipelines.crag import CRAGPipeline

pipeline = CRAGPipeline(
    retriever=팀원B의_mmr_retriever,           # 팀원 B 구현
    embedding_model=팀원A의_advanced_embedding, # 팀원 A 구현
    vector_store=팀원B의_벡터저장소,           # 팀원 B 구현
    llm_client=기본_llm,
    web_search=기본_web_search,
    config=config,
)
```

## 📝 설정 사용법

### 전역 설정
```python
from common.config import CommonConfig, get_config

# 개발 환경 설정
config = get_config("dev")

# 모델 설정 접근
print(config.model.llm_model)           # "gpt-4o-mini"
print(config.model.embedding_model)    # "text-embedding-3-small"

# 파이프라인 설정
print(config.pipeline.top_k)            # 5
print(config.pipeline.use_web_search)  # True
```

### 커스텀 설정
```python
from common.config import CommonConfig, ModelConfig, PipelineConfig

# 커스텀 설정 생성
custom_config = CommonConfig(
    model=ModelConfig(
        llm_model="claude-3-opus",
        embedding_model="text-embedding-3-large",
    ),
    pipeline=PipelineConfig(
        top_k=10,
        use_web_search=True,
    )
)
```

## 🧪 테스트 방법

### 단위 테스트 (각 팀원)
```python
# test_my_retriever.py
from extensions.retrievers.my_retriever import MyRetriever

def test_retriever():
    retriever = MyRetriever(vector_store)
    results = retriever.retrieve("테스트 쿼리", top_k=5)
    
    assert len(results) <= 5
    assert all(isinstance(r, RetrievalResult) for r in results)
    print("✅ 테스트 통과")
```

### 통합 테스트 (전체 파이프라인)
```python
# test_pipeline_integration.py
from common.pipelines import SimpleRAGPipeline
from extensions.retrievers.my_retriever import MyRetriever

def test_pipeline():
    pipeline = SimpleRAGPipeline(
        retriever=MyRetriever(vector_store),
        ...
    )
    
    response = pipeline.process("테스트 질문")
    
    assert response['success'] == True
    assert len(response['answer']) > 0
    assert 'sources' in response
    print("✅ 통합 테스트 통과")
```

## 📚 주요 클래스 API

### BaseEmbedding
```python
# 임베딩 모델 인터페이스
class BaseEmbedding(ABC):
    def embed_text(text: str) -> List[float]
    def embed_batch(texts: List[str]) -> List[List[float]]
    def get_embedding_dimension() -> int
```

### BaseRetriever
```python
# 검색기 인터페이스
class BaseRetriever(ABC):
    def retrieve(query: str, top_k: int) -> List[RetrievalResult]
```

### BaseRAGPipeline
```python
# RAG 파이프라인 인터페이스
class BaseRAGPipeline(ABC):
    def retrieve(query: str, top_k: int) -> List[RetrievalResult]
    def grade(query: str, documents) -> Tuple[List[bool], Dict]
    def generate(query: str, documents) -> str
    def process(query: str, **kwargs) -> Dict
```

### QueryRequest & QueryResponse
```python
# 요청
request = QueryRequest(
    query="강아지 피부 질환?",
    query_type=QueryType.FACTUAL,
    top_k=5,
    temperature=0.7,
    include_sources=True,
)

# 응답
response = QueryResponse(
    query=request.query,
    answer="답변...",
    sources=[SourceInfo(...)],
    response_time=2.34,
)
```

## 🔍 로깅 및 디버깅

### 로깅 설정
```python
from common.utils import setup_logging

logger = setup_logging()

logger.info("ℹ️ 정보")
logger.warning("⚠️ 경고")
logger.error("❌ 오류")
logger.debug("🐛 디버그")
```

### 디버그 정보 확인
```python
response = pipeline.process("질문", include_debug_info=True)

print(response['debug_info'])
# {
#     'relevant_count': 3,
#     'total_count': 5,
#     'relevance_scores': [0.8, 0.75, 0.7, 0.4, 0.3],
#     ...
# }
```

## 💡 모범 사례

### 1. 에러 처리
```python
try:
    result = self.vector_store.search(query, top_k)
except Exception as e:
    logger.error(f"검색 오류: {e}")
    raise  # 또는 폴백 로직
```

### 2. 캐싱 활용
```python
from common.utils import cache_result

@cache_result
def expensive_embedding(text: str):
    return self.model.embed(text)
```

### 3. 타입 힌팅
```python
from typing import List, Dict, Any, Optional
from common.models import Document, QueryResponse

def process_documents(
    documents: List[Document],
    query: str,
    top_k: int = 5
) -> QueryResponse:
    pass
```

### 4. 문서화
```python
class MyRetriever(BaseRetriever):
    """
    MMR 검색기
    
    이 검색기는 다양성을 고려하여 문서를 검색합니다.
    
    Args:
        vector_store: 벡터 저장소
        lambda_mult: 다양성 계수 (0~1)
    
    Returns:
        검색 결과 리스트
    
    Example:
        >>> retriever = MyRetriever(vector_store)
        >>> results = retriever.retrieve("쿼리")
    """
```

## 🤝 협업 워크플로우

### 1. 기능 선택
```
팀원이 자신의 고도화 영역 선택
예: "MMR 검색기" 또는 "CRAG 파이프라인"
```

### 2. 인터페이스 확인
```python
# base.py에서 구현할 인터페이스 확인
class BaseRetriever(ABC):
    @abstractmethod
    def retrieve(self, query: str, top_k: int = 5) -> List[RetrievalResult]:
        pass
```

### 3. 구현
```python
class MyRetriever(BaseRetriever):
    def retrieve(self, query: str, top_k: int = 5):
        # 팀원이 고도화된 로직 구현
        pass
```

### 4. 테스트
```bash
# 단위 테스트
python test_my_retriever.py

# 통합 테스트
python test_pipeline_integration.py
```

### 5. 등록
```python
# extensions/__init__.py
from .retrievers.my_retriever import MyRetriever

__all__ = ["MyRetriever"]
```

### 6. 사용
```python
from extensions import MyRetriever
from common.pipelines import SimpleRAGPipeline

pipeline = SimpleRAGPipeline(
    retriever=MyRetriever(vector_store),
    ...
)
```

## 📞 FAQ

### Q1: 공통 모듈을 수정해야 할 경우?
**A:** 기본 인터페이스는 수정 금지. 버그 수정이나 기능 추가 필요 시 프로젝트 리드와 상담.

### Q2: 다른 팀원의 구현을 사용할 수 있나?
**A:** 물론! `extensions/__init__.py`에 등록되면 누구나 사용 가능.

```python
from extensions import MyRetriever, AdvancedEmbedding, CRAGPipeline

# 조합 사용 가능
pipeline = CRAGPipeline(
    retriever=MyRetriever(...),
    embedding_model=AdvancedEmbedding(...),
)
```

### Q3: 성능 벤치마킹은?
**A:** `metrics` 딕셔너리에서 응답 시간 등 확인 가능.

```python
response = pipeline.process("질문")
print(response['metrics'])
# {
#     'retrieval_time': '0.45s',
#     'grading_time': '1.23s',
#     'generation_time': '2.10s',
#     'total_time': '3.78s',
# }
```

### Q4: 새로운 컴포넌트 추가하고 싶으면?
**A:** 공통 모듈에서 `BaseXXX` 인터페이스를 정의한 후 `extensions/`에 구현.

## 📖 참고 자료

- [common/base.py](./base.py) - 인터페이스 정의
- [common/models.py](./models.py) - 데이터 구조
- [common/config.py](./config.py) - 설정
- [common/pipelines.py](./pipelines.py) - 기본 파이프라인
- [extensions/example_implementations.py](./extensions/example_implementations.py) - 구현 예시
- [extensions/README.md](./extensions/README.md) - 확장 가이드

## 🎓 학습 경로

```
1. 공통 모듈 이해
   └─ base.py, config.py, models.py 읽기

2. SimpleRAGPipeline 분석
   └─ pipelines.py 코드 분석

3. 예시 구현 검토
   └─ extensions/example_implementations.py 실행

4. 자신의 고도화 영역 구현
   └─ BaseXXX 상속 → 구현 → 테스트

5. 팀원 코드와 통합
   └─ 함께 테스트 → 최적화
```

---

**질문이나 제안이 있으신가요?** 프로젝트 리드에 연락하세요! 🚀


