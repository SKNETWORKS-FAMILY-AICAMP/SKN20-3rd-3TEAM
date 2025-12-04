# 확장 포인트 (Extensions)

이 디렉토리는 각 팀원이 공통 모듈을 기반으로 **고도화하고 싶은 부분을 담당**할 수 있는 공간입니다.

## 📁 디렉토리 구조

```
extensions/
├── __init__.py              # 확장 모듈 초기화
├── embeddings/              # 임베딩 모델 고도화
│   ├── openai_embedding.py  # OpenAI Embeddings 구현
│   ├── huggingface_embedding.py  # HuggingFace Embeddings
│   └── custom_embedding.py  # 커스텀 임베딩
├── vectorstores/            # 벡터 저장소 고도화
│   ├── chroma_store.py      # Chroma 구현
│   ├── pinecone_store.py    # Pinecone 구현
│   └── weaviate_store.py    # Weaviate 구현
├── retrievers/              # 검색 알고리즘 고도화
│   ├── simple_retriever.py  # Top-K 검색
│   ├── mmr_retriever.py     # MMR (Maximum Marginal Relevance)
│   ├── bm25_retriever.py    # BM25 검색
│   └── hybrid_retriever.py  # 하이브리드 검색
├── llm_clients/             # LLM 클라이언트 고도화
│   ├── openai_client.py     # OpenAI API
│   ├── claude_client.py     # Anthropic Claude
│   └── local_llm_client.py  # 로컬 LLM (Ollama)
├── web_search/              # 웹 검색 고도화
│   ├── tavily_search.py     # Tavily API
│   ├── google_search.py     # Google Search
│   └── duckduckgo_search.py # DuckDuckGo
├── pipelines/               # RAG 파이프라인 고도화
│   ├── crag_pipeline.py     # CRAG (Corrective RAG)
│   ├── multihop_pipeline.py # Multi-hop RAG
│   ├── agent_pipeline.py    # Agent-based RAG
│   └── optimized_pipeline.py # 비용 최적화 RAG
└── modules/                 # 도메인별 특화 모듈
    ├── medical_rag.py       # 의료 도메인 RAG
    ├── legal_rag.py         # 법률 도메인 RAG
    └── finance_rag.py       # 금융 도메인 RAG
```

## 🎯 팀원별 담당 영역 예시

### 팀원 A: 임베딩 모델 최적화
- `extensions/embeddings/` 폴더에서 작업
- 다양한 임베딩 모델 구현
- 성능 벤치마킹

```python
from common.base import BaseEmbedding

class AdvancedEmbedding(BaseEmbedding):
    def embed_text(self, text: str) -> List[float]:
        # 구현
        pass
```

### 팀원 B: 검색 알고리즘 개선
- `extensions/retrievers/` 폴더에서 작업
- MMR, BM25, 하이브리드 검색 구현
- 검색 성능 최적화

```python
from common.base import BaseRetriever

class AdvancedRetriever(BaseRetriever):
    def retrieve(self, query: str, top_k: int = 5, **kwargs):
        # 구현
        pass
```

### 팀원 C: RAG 파이프라인 고도화
- `extensions/pipelines/` 폴더에서 작업
- CRAG, Multi-hop 등 고급 패턴 구현
- 웹 검색 추가
- 답변 품질 검사

```python
from common.pipelines import SimpleRAGPipeline

class CRAGPipeline(SimpleRAGPipeline):
    def process(self, query: str, **kwargs):
        # CRAG 로직 추가
        pass
```

### 팀원 D: 도메인 특화 모듈
- `extensions/modules/` 폴더에서 작업
- 특정 도메인(의료, 법률 등)에 특화된 RAG 구현
- 도메인별 프롬프트 튜닝
- 도메인별 평가 메트릭

```python
from common.pipelines import SimpleRAGPipeline

class MedicalRAG(SimpleRAGPipeline):
    def _get_generation_prompt(self, query: str, context: str) -> str:
        # 의료 도메인 특화 프롬프트
        pass
```

## 🚀 작업 방식

### 1. 브랜치 생성
```bash
git checkout -b feature/embeddings-optimization
```

### 2. 공통 모듈 import
```python
from common.base import BaseEmbedding, BaseRetriever, BaseRAGPipeline
from common.config import CommonConfig, PipelineConfig
from common.models import Document, QueryRequest, QueryResponse
from common.utils import setup_logging, load_json, save_json
```

### 3. 인터페이스 구현
```python
class MyAdvancedEmbedding(BaseEmbedding):
    def embed_text(self, text: str) -> List[float]:
        # 구현
        pass
    
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        # 구현
        pass
    
    def get_embedding_dimension(self) -> int:
        # 구현
        pass
```

### 4. 테스트
```python
# test_advanced_embedding.py
from extensions.embeddings.my_embedding import MyAdvancedEmbedding

def test_embedding():
    embedding = MyAdvancedEmbedding("model_name")
    result = embedding.embed_text("테스트 텍스트")
    assert len(result) == embedding.get_embedding_dimension()
    print("✅ 테스트 통과")
```

### 5. 통합 테스트
```python
# test_integration.py
from common.pipelines import SimpleRAGPipeline
from extensions.embeddings.my_embedding import MyAdvancedEmbedding
from extensions.retrievers.my_retriever import MyRetriever

# 각 컴포넌트가 함께 잘 작동하는지 확인
pipeline = SimpleRAGPipeline(
    retriever=MyRetriever(...),
    embedding_model=MyAdvancedEmbedding(...),
    vector_store=...,
    llm_client=...
)

response = pipeline.process("테스트 질문")
assert response['success'] == True
```

## 📋 체크리스트

### 구현 시 확인사항
- [ ] `BaseXXX` 추상 클래스를 상속했는가?
- [ ] 모든 추상 메서드를 구현했는가?
- [ ] 타입 힌팅을 작성했는가?
- [ ] 주석/docstring을 작성했는가?
- [ ] 에러 처리를 했는가?
- [ ] 로깅을 추가했는가?
- [ ] 유닛 테스트를 작성했는가?
- [ ] 통합 테스트를 실행했는가?

### 제출 전 확인사항
- [ ] 공통 모듈에 의존성을 추가하지 않았는가?
- [ ] 기본 인터페이스를 변경하지 않았는가?
- [ ] 다른 팀원의 작업과 충돌하지 않는가?
- [ ] 코드 스타일이 일관되는가?
- [ ] 성능 테스트를 실행했는가?

## 📚 공통 모듈 API

### 기본 클래스 (common.base)
- `BaseEmbedding`: 임베딩 모델 인터페이스
- `BaseVectorStore`: 벡터 저장소 인터페이스
- `BaseRetriever`: 검색기 인터페이스
- `BaseRAGPipeline`: RAG 파이프라인 인터페이스
- `BaseLLMClient`: LLM 클라이언트 인터페이스
- `BaseWebSearch`: 웹 검색 인터페이스

### 데이터 모델 (common.models)
- `Document`: 문서
- `QueryRequest`: 질문 요청
- `QueryResponse`: 질문 응답
- `SourceInfo`: 출처 정보
- `ChatMessage`: 채팅 메시지
- `ChatHistory`: 대화 기록

### 설정 (common.config)
- `CommonConfig`: 전체 설정
- `ModelConfig`: 모델 설정
- `PipelineConfig`: 파이프라인 설정
- `UIConfig`: UI 설정

### 유틸리티 (common.utils)
- `setup_logging()`: 로깅 설정
- `load_json()`, `save_json()`: JSON 파일 I/O
- `chunk_text()`: 텍스트 청킹
- `hash_text()`: 해시 생성
- `cache_result`: 캐싱 데코레이터
- 등등...

## 🔗 통합 가이드

각 팀원이 구현한 확장 모듈은 `extensions/__init__.py`에 등록되어야 합니다:

```python
# extensions/__init__.py
from .embeddings.my_embedding import MyAdvancedEmbedding
from .retrievers.my_retriever import MyRetriever
from .pipelines.my_pipeline import MyAdvancedPipeline

__all__ = [
    "MyAdvancedEmbedding",
    "MyRetriever",
    "MyAdvancedPipeline",
]
```

## 💡 팁 & 트릭

### 로깅 활용
```python
import logging
logger = logging.getLogger(__name__)

logger.info("ℹ️ 정보")
logger.warning("⚠️ 경고")
logger.error("❌ 오류")
```

### 설정 사용
```python
from common.config import get_config

config = get_config("dev")
print(config.model.llm_model)
print(config.pipeline.top_k)
```

### 캐싱 활용
```python
from common.utils import cache_result

@cache_result
def expensive_operation(data):
    # 시간 오래 걸리는 작업
    return result
```

### 타입 힌팅
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

## 🤝 협업 규칙

1. **메인 브랜치 보호**: 직접 commit 금지, PR 필수
2. **코드 리뷰**: 최소 1명의 코드 리뷰 필수
3. **테스트**: 모든 기능은 테스트 커버리지 80% 이상
4. **문서화**: 공개 API는 docstring 필수
5. **커밋 메시지**: Conventional Commits 형식 준수

## 📞 지원

- 공통 모듈 문제: 프로젝트 리드
- 통합 문제: 아키텍처 리드
- 도메인 질문: 해당 도메인 전문가



