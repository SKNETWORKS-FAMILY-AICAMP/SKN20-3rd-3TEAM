# 🎯 RAG 공통 모듈 (Common Module)

## 📌 개요

**공통 모듈**은 프로젝트 전체의 기준이 되는 RAG(Retrieval-Augmented Generation) 시스템의 뼈대입니다.

각 팀원은 이 공통 기준을 기반으로 **자신이 고도화하고 싶은 부분을 담당**하여 보완합니다.

### 핵심 원칙
```
┌─────────────────────────┐
│    공통 모듈 (기준)      │  ← 모든 팀원이 사용
│   ├─ 인터페이스         │     (수정 불가)
│   ├─ 데이터 구조        │
│   ├─ 설정               │
│   └─ 기본 구현          │
└─────────────────────────┘
         ↓↓↓
┌─────────────────────────────────┐
│  확장 모듈 (팀원 고도화)          │  ← 각자 작업
│  ├─ 팀원 A: 임베딩 최적화       │     (수정 가능)
│  ├─ 팀원 B: 검색 개선           │
│  ├─ 팀원 C: 파이프라인 고도화   │
│  └─ 팀원 D: 도메인 특화         │
└─────────────────────────────────┘
```

## 🚀 빠른 시작

### 1단계: 의존성 설치
```bash
pip install -r requirements.txt
```

### 2단계: 환경 변수 설정
```bash
export OPENAI_API_KEY="sk-..."
export TAVILY_API_KEY="tvly-..."
```

### 3단계: 공통 모듈 사용
```python
from common.base import BaseEmbedding, BaseRetriever
from common.config import CommonConfig
from common.models import QueryRequest, QueryResponse
from common.pipelines import SimpleRAGPipeline
from common.utils import setup_logging

# 로깅 설정
logger = setup_logging()

# 설정 로드
config = CommonConfig()

# 기본 파이프라인 실행
response = pipeline.process("질문")
print(response['answer'])
```

## 📁 구조

```
common/
├── __init__.py              # 패키지 초기화
├── base.py ⭐⭐⭐          # 모든 인터페이스 정의 (핵심)
├── config.py                # 설정 및 상수
├── models.py                # 데이터 구조
├── pipelines.py             # 기본 RAG 파이프라인
├── utils.py                 # 유틸리티 함수
│
├── README.md                # 이 파일
├── COMMON_MODULE_GUIDE.md   # 완전 가이드 ⭐⭐
├── STRUCTURE.md             # 구조 설명
│
└── extensions/              # 팀원 작업 영역
    ├── __init__.py
    ├── README.md            # 확장 가이드 ⭐
    ├── example_implementations.py  # 예시 코드 ⭐
    ├── embeddings/          # 팀원 A
    ├── retrievers/          # 팀원 B
    ├── pipelines/           # 팀원 C
    └── modules/             # 팀원 D
```

## 🔑 핵심 개념

### 1. 인터페이스 기반 설계
모든 컴포넌트는 `BaseXXX` 추상 클래스를 따릅니다.

```python
# base.py에 정의된 인터페이스
class BaseEmbedding(ABC):
    @abstractmethod
    def embed_text(self, text: str) -> List[float]: pass
    
    @abstractmethod
    def embed_batch(self, texts: List[str]) -> List[List[float]]: pass
```

### 2. 플러그인 아키텍처
팀원들은 `extensions/`에서 자유롭게 구현하고 교체 가능합니다.

```python
# 기본 구현
from common.pipelines import SimpleRAGPipeline

# 팀원 B의 고도화 구현
from extensions.retrievers.mmr_retriever import MMRRetriever

# 조합 사용 가능
pipeline = SimpleRAGPipeline(
    retriever=MMRRetriever(...),  # 팀원 B의 구현
    ...
)
```

### 3. 공통 계약
모든 구현은 동일한 입출력 형식을 따릅니다.

```python
# 입력: QueryRequest
request = QueryRequest(query="질문", top_k=5)

# 처리: SimpleRAGPipeline 또는 고도화 파이프라인
response = pipeline.process(request.query)

# 출력: QueryResponse
# {
#     'query': '질문',
#     'answer': '답변...',
#     'sources': [...],
#     'metrics': {...}
# }
```

## 👥 팀원별 역할

### 팀원 A: 임베딩 모델 최적화
**담당 영역**: `common/extensions/embeddings/`

```python
class AdvancedEmbedding(BaseEmbedding):
    """더 빠르고 정확한 임베딩 구현"""
    def embed_text(self, text: str) -> List[float]:
        # 고도화 로직
        pass
```

**목표**: 
- 다양한 임베딩 모델 지원 (OpenAI, HuggingFace 등)
- 성능 최적화 (배치 처리, 캐싱)
- 임베딩 품질 개선

### 팀원 B: 검색 알고리즘 개선
**담당 영역**: `common/extensions/retrievers/`

```python
class MMRRetriever(BaseRetriever):
    """다양성을 고려한 MMR 검색"""
    def retrieve(self, query: str, top_k: int) -> List[RetrievalResult]:
        # MMR 알고리즘
        pass
```

**목표**:
- MMR, BM25, 하이브리드 검색 구현
- 검색 성능 최적화
- 결과 다양성 향상

### 팀원 C: RAG 파이프라인 고도화
**담당 영역**: `common/extensions/pipelines/`, `llm_clients/`, `web_search/`

```python
class CRAGPipeline(SimpleRAGPipeline):
    """CRAG (Corrective RAG) 구현"""
    def process(self, query: str, **kwargs):
        # CRAG 로직: 웹 검색 추가, 재시도 등
        pass
```

**목표**:
- CRAG, Multi-hop RAG 구현
- 웹 검색 통합
- 답변 품질 검사 추가
- 비용 최적화

### 팀원 D: 도메인 특화 모듈
**담당 영역**: `common/extensions/modules/`

```python
class MedicalRAG(SimpleRAGPipeline):
    """의료 도메인 특화 RAG"""
    def _get_generation_prompt(self, query: str, context: str) -> str:
        # 의료 도메인 특화 프롬프트
        pass
```

**목표**:
- 의료, 법률, 금융 등 도메인별 특화
- 도메인별 프롬프트 튜닝
- 도메인별 평가 메트릭

## 📚 주요 파일 설명

### base.py ⭐⭐⭐ (가장 중요)
모든 구현의 기준이 되는 추상 클래스들을 정의합니다.

**포함 내용**:
- `BaseEmbedding`: 임베딩 모델 인터페이스
- `BaseVectorStore`: 벡터 저장소 인터페이스
- `BaseRetriever`: 검색기 인터페이스
- `BaseRAGPipeline`: RAG 파이프라인 인터페이스
- `BaseLLMClient`: LLM 클라이언트 인터페이스
- `BaseWebSearch`: 웹 검색 인터페이스

```python
from common.base import (
    BaseEmbedding,
    BaseRetriever,
    BaseRAGPipeline,
)

# 팀원이 상속하여 구현
class MyEmbedding(BaseEmbedding):
    pass
```

### config.py
프로젝트 전체의 설정을 중앙에서 관리합니다.

**주요 설정**:
- `ModelConfig`: LLM, 임베딩 모델 설정 + API 키
- `PipelineConfig`: Top-K, 관련성 임계값, 웹 검색 설정
- `UIConfig`: UI/UX 설정
- `Constants`: 프로젝트 상수 (프롬프트, 임계값 등)

```python
from common.config import CommonConfig, get_config

config = get_config("dev")
print(config.model.llm_model)           # gpt-4o-mini
print(config.pipeline.top_k)            # 5
print(config.pipeline.use_web_search)   # True
```

### models.py
전체 파이프라인에서 사용할 데이터 구조를 정의합니다.

**주요 모델**:
- `Document`: 문서
- `QueryRequest`: 질문 요청
- `QueryResponse`: 질문 응답 (답변 + 출처 + 메트릭)
- `SourceInfo`: 출처 정보
- `ChatMessage` & `ChatHistory`: 대화 기록

```python
from common.models import QueryRequest, QueryResponse

# 요청 생성
request = QueryRequest(query="질문", top_k=5)

# 응답 생성
response = QueryResponse(
    query="질문",
    answer="답변...",
    sources=[...],
    response_time=2.34
)

# JSON으로 변환
print(response.to_json_string())
```

### pipelines.py
공통 기준이 되는 단순 RAG 파이프라인입니다.

**처리 흐름**:
1. **Retrieve**: 쿼리와 유사한 문서 검색
2. **Grade**: 문서 관련성 평가 (선택사항)
3. **Generate**: 관련 문서 기반 답변 생성
4. **Return**: 답변 + 출처 반환

```python
from common.pipelines import SimpleRAGPipeline

# 팀원들의 구현으로 초기화
pipeline = SimpleRAGPipeline(
    retriever=retriever_instance,
    embedding_model=embedding_instance,
    vector_store=vectorstore_instance,
    llm_client=llm_instance,
)

# 처리 실행
response = pipeline.process("사용자 질문")
print(response['answer'])
print(response['sources'])
print(response['metrics'])
```

### utils.py
공통 유틸리티 함수를 제공합니다.

**주요 함수**:
- `setup_logging()`: 로깅 설정
- `load_json()`, `save_json()`: JSON 파일 I/O
- `chunk_text()`: 텍스트 청킹
- `hash_text()`: 해시 생성
- `cache_result`: 캐싱 데코레이터
- `format_time()`, `format_size()`: 형식 변환
- 등등...

```python
from common.utils import setup_logging, load_json, cache_result

# 로깅 설정
logger = setup_logging()

# JSON 로드
data = load_json("config.json")

# 캐싱
@cache_result
def expensive_operation(data):
    return result
```

## 📖 다음 단계

### 1단계: 구조 이해 (15분)
```bash
# 다음 파일들을 순서대로 읽기
1. common/README.md (이 파일)
2. common/STRUCTURE.md
3. common/COMMON_MODULE_GUIDE.md
```

### 2단계: 코드 분석 (1시간)
```python
# 다음 파일들을 코드로 분석
1. common/base.py - 인터페이스 이해
2. common/models.py - 데이터 구조 이해
3. common/pipelines.py - 기본 처리 흐름 이해
```

### 3단계: 예시 실행 (30분)
```bash
python common/extensions/example_implementations.py
```

### 4단계: 자신의 구현 시작
```bash
# 담당 영역 선택 및 구현 시작
# extensions/README.md 참고하여 진행
```

## 🔍 코드 예시

### 기본 사용법
```python
from common.pipelines import SimpleRAGPipeline
from common.config import CommonConfig
from common.utils import setup_logging

# 1. 로깅 설정
logger = setup_logging()

# 2. 설정 로드
config = CommonConfig()

# 3. 컴포넌트 초기화 (팀원 구현 사용)
from extensions.embeddings.openai_embedding import OpenAIEmbedding
from extensions.retrievers.mmr_retriever import MMRRetriever

embedding = OpenAIEmbedding(model_name="text-embedding-3-small")
retriever = MMRRetriever(vector_store)

# 4. 파이프라인 생성
pipeline = SimpleRAGPipeline(
    retriever=retriever,
    embedding_model=embedding,
    vector_store=vector_store,
    llm_client=llm_client,
    config=config.pipeline,
)

# 5. 처리 실행
response = pipeline.process("사용자 질문", top_k=5)

# 6. 결과 확인
print(f"답변: {response['answer']}")
print(f"응답 시간: {response['metrics']['total_time']}")
for source in response['sources']:
    print(f"  - {source['title']}")
```

### 팀원 구현 예시
```python
# 팀원 B의 고도화 검색기
from common.base import BaseRetriever
from common.models import RetrievalResult

class MMRRetriever(BaseRetriever):
    """MMR 기반 검색기"""
    
    def retrieve(self, query: str, top_k: int = 5, **kwargs):
        # Step 1: 기본 검색
        candidates = self.vector_store.search(query, top_k * 3)
        
        # Step 2: MMR 재순위
        results = self._mmr_rerank(candidates, top_k)
        
        return results
    
    def _mmr_rerank(self, candidates, top_k):
        # MMR 알고리즘 구현
        pass
```

## ⚙️ 설정 예시

```python
from common.config import CommonConfig, ModelConfig, PipelineConfig

# 기본 설정 사용
config = CommonConfig()

# 커스텀 설정
custom_config = CommonConfig(
    model=ModelConfig(
        llm_model="claude-3-opus",
        embedding_model="text-embedding-3-large",
        llm_temperature=0.5,
    ),
    pipeline=PipelineConfig(
        top_k=10,
        use_web_search=True,
        relevance_threshold=0.6,
    )
)

# 환경별 설정
from common.config import get_config
config = get_config("prod")  # 프로덕션 설정 로드
```

## 🧪 테스트

### 단위 테스트
```bash
python -m pytest tests/test_base.py
python -m pytest tests/test_pipelines.py
```

### 통합 테스트
```bash
python common/extensions/example_implementations.py
```

## 📞 FAQ

### Q: 공통 모듈을 수정할 수 있나요?
**A**: 아니오. 공통 모듈은 모든 팀원의 기준입니다. 수정이 필요하면 프로젝트 리드와 상담하세요.

### Q: 자신의 구현을 어디에 저장하나요?
**A**: `common/extensions/` 폴더의 해당 영역에 저장하세요.
- 팀원 A: `extensions/embeddings/`
- 팀원 B: `extensions/retrievers/`
- 팀원 C: `extensions/pipelines/`
- 팀원 D: `extensions/modules/`

### Q: 다른 팀원의 구현을 사용할 수 있나요?
**A**: 네! 각자 `extensions/__init__.py`에 등록하면 모두가 사용 가능합니다.

### Q: 성능을 측정할 수 있나요?
**A**: 네! 모든 응답에는 `metrics` 정보가 포함됩니다.
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

## 🎓 학습 경로

```
1일차: 공통 모듈 이해
   └─ README.md, STRUCTURE.md 읽기

2일차: 코드 분석
   └─ base.py, config.py, models.py 분석

3일차: 파이프라인 학습
   └─ pipelines.py 코드 분석

4일차: 예시 실행
   └─ example_implementations.py 실행

5일차부터: 자신의 구현 시작
   └─ extensions/README.md 참고
```

## 📚 참고 자료

| 파일 | 설명 | 읽기 순서 |
|------|------|----------|
| `README.md` | 이 파일 | 1️⃣ |
| `STRUCTURE.md` | 구조 설명 | 2️⃣ |
| `COMMON_MODULE_GUIDE.md` | 완전 가이드 | 3️⃣ |
| `base.py` | 인터페이스 | 4️⃣ |
| `config.py` | 설정 | 5️⃣ |
| `models.py` | 데이터 구조 | 6️⃣ |
| `pipelines.py` | 기본 파이프라인 | 7️⃣ |
| `extensions/README.md` | 확장 가이드 | 8️⃣ |
| `extensions/example_implementations.py` | 예시 코드 | 9️⃣ |

## 🚀 다음 액션

1. **지금 바로**: [STRUCTURE.md](./STRUCTURE.md)를 읽으세요
2. **15분 후**: [COMMON_MODULE_GUIDE.md](./COMMON_MODULE_GUIDE.md)를 읽으세요
3. **30분 후**: 자신의 구현 영역을 결정하세요
4. **1시간 후**: [extensions/README.md](./extensions/README.md)를 참고하여 시작하세요
5. **1일 후**: 첫 번째 기능을 완성하세요

---

**질문이 있으신가요?** 프로젝트 리드에 연락하세요! 🎯

Happy coding! 💻✨


