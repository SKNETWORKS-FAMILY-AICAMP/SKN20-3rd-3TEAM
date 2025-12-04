# 🏗️ 공통 모듈 구조

## 📂 디렉토리 트리

```
common/
│
├── __init__.py
│   └─ 공통 모듈 패키지 초기화
│      모든 팀원이 import할 주요 클래스 정의
│
├── base.py ⭐⭐⭐ 가장 중요
│   └─ 모든 인터페이스 정의
│      - BaseEmbedding: 임베딩 모델
│      - BaseVectorStore: 벡터 저장소
│      - BaseRetriever: 검색기
│      - BaseRAGPipeline: RAG 파이프라인
│      - BaseLLMClient: LLM 클라이언트
│      - BaseWebSearch: 웹 검색
│
├── config.py
│   └─ 설정 및 상수
│      - DataConfig: 데이터 설정
│      - ModelConfig: 모델 설정 (API 키 포함)
│      - PipelineConfig: 파이프라인 설정
│      - UIConfig: UI 설정
│      - CommonConfig: 통합 설정
│      - Constants: 프로젝트 상수
│
├── models.py
│   └─ 데이터 구조 정의
│      - Document: 문서
│      - QueryRequest: 질문 요청
│      - QueryResponse: 질문 응답
│      - SourceInfo: 출처 정보
│      - ChatMessage: 채팅 메시지
│      - ChatHistory: 대화 기록
│      - GradeResult: 평가 결과
│      - PipelineMetrics: 성능 메트릭
│
├── pipelines.py
│   └─ 기본 RAG 파이프라인 구현
│      - SimpleRAGPipeline: 공통 기준 파이프라인
│        ├─ retrieve(): 문서 검색
│        ├─ grade(): 관련성 평가
│        ├─ generate(): 답변 생성
│        └─ process(): 전체 처리
│
├── utils.py
│   └─ 공통 유틸리티 함수
│      - setup_logging(): 로깅 설정
│      - load_json(), save_json(): JSON I/O
│      - chunk_text(): 텍스트 청킹
│      - hash_text(): 해시 생성
│      - cache_result: 캐싱 데코레이터
│      - format_time(): 시간 포맷
│      - 등등...
│
├── COMMON_MODULE_GUIDE.md ⭐
│   └─ 공통 모듈 완전 가이드
│
├── STRUCTURE.md (이 파일)
│   └─ 모듈 구조 설명
│
└── extensions/
    │
    ├── __init__.py
    │   └─ 팀원들이 구현한 모듈 등록
    │
    ├── README.md ⭐
    │   └─ 확장 모듈 작업 가이드
    │
    ├── example_implementations.py ⭐
    │   └─ 팀원들이 참고할 구현 예시
    │      - ExampleEmbedding
    │      - ExampleVectorStore
    │      - ExampleRetriever
    │      - ExampleLLMClient
    │      - ExampleWebSearch
    │      - ExampleAdvancedPipeline
    │
    ├── embeddings/              (팀원 A 담당 영역)
    │   ├── __init__.py
    │   ├── openai_embedding.py
    │   ├── huggingface_embedding.py
    │   └── custom_embedding.py
    │
    ├── vectorstores/            (팀원 B 담당 영역)
    │   ├── __init__.py
    │   ├── chroma_store.py
    │   ├── pinecone_store.py
    │   └── weaviate_store.py
    │
    ├── retrievers/              (팀원 B 담당 영역)
    │   ├── __init__.py
    │   ├── simple_retriever.py
    │   ├── mmr_retriever.py
    │   ├── bm25_retriever.py
    │   └── hybrid_retriever.py
    │
    ├── llm_clients/             (팀원 C 담당 영역)
    │   ├── __init__.py
    │   ├── openai_client.py
    │   ├── claude_client.py
    │   └── local_llm_client.py
    │
    ├── web_search/              (팀원 C 담당 영역)
    │   ├── __init__.py
    │   ├── tavily_search.py
    │   ├── google_search.py
    │   └── duckduckgo_search.py
    │
    ├── pipelines/               (팀원 C 담당 영역)
    │   ├── __init__.py
    │   ├── crag_pipeline.py
    │   ├── multihop_pipeline.py
    │   ├── agent_pipeline.py
    │   └── optimized_pipeline.py
    │
    └── modules/                 (팀원 D 담당 영역)
        ├── __init__.py
        ├── medical_rag.py
        ├── legal_rag.py
        └── finance_rag.py
```

## 🔄 의존성 관계도

```
공통 모듈 (필수)
    ↓
  base.py ←─── 모든 것의 기초
    ↓
 ┌─────────────────────────────────────┐
 ├─→ config.py (설정)                  │
 ├─→ models.py (데이터 구조)           │
 ├─→ utils.py (유틸리티)               │
 └─→ pipelines.py (기본 파이프라인)    │
    ↓
extensions/ (팀원 구현)
    ↓
 ┌───────────────────────────────┐
 ├─ embeddings/                  │
 ├─ retrievers/                  │ ← 서로 독립적
 ├─ llm_clients/                 │
 ├─ pipelines/                   │
 └─ modules/                     │
    └───────────────────────────────┘
```

## 🎯 각 파일의 역할

### base.py (인터페이스 정의)
```
┌──────────────────────────────────────┐
│ base.py - 모든 구현의 기준            │
├──────────────────────────────────────┤
│                                      │
│ BaseEmbedding                        │
│   ├─ embed_text()                    │
│   ├─ embed_batch()                   │
│   └─ get_embedding_dimension()       │
│                                      │
│ BaseVectorStore                      │
│   ├─ add_documents()                 │
│   ├─ search()                        │
│   ├─ delete_documents()              │
│   └─ clear()                         │
│                                      │
│ BaseRetriever                        │
│   └─ retrieve()                      │
│                                      │
│ BaseRAGPipeline                      │
│   ├─ retrieve()                      │
│   ├─ grade()                         │
│   ├─ generate()                      │
│   └─ process()                       │
│                                      │
│ BaseLLMClient                        │
│   ├─ generate()                      │
│   └─ grade()                         │
│                                      │
│ BaseWebSearch                        │
│   └─ search()                        │
│                                      │
└──────────────────────────────────────┘
     ↓ 팀원들이 상속하여 구현
┌──────────────────────────────────────┐
│ 팀원 구현들                           │
│ ├─ OpenAIEmbedding(BaseEmbedding)    │
│ ├─ ChromaStore(BaseVectorStore)      │
│ ├─ MMRRetriever(BaseRetriever)       │
│ ├─ CRAGPipeline(BaseRAGPipeline)     │
│ ├─ OpenAIClient(BaseLLMClient)       │
│ └─ TavilySearch(BaseWebSearch)       │
└──────────────────────────────────────┘
```

### models.py (데이터 구조)
```
QueryRequest               QueryResponse
├─ query: str             ├─ query: str
├─ query_type: Enum       ├─ answer: str
├─ language: str          ├─ sources: List[SourceInfo]
├─ top_k: int             ├─ response_time: float
├─ temperature: float     ├─ retrieval_time: float
├─ include_sources: bool  ├─ generation_time: float
└─ metadata: Dict         └─ metadata: Dict
                
Document                  SourceInfo
├─ id: str               ├─ title: str
├─ content: str          ├─ url: str
├─ title: str            ├─ document_id: str
├─ source: Enum          ├─ similarity_score: float
├─ metadata: Dict        ├─ relevance_score: float
└─ embedding: List       └─ metadata: Dict

ChatMessage              ChatHistory
├─ role: str            ├─ session_id: str
├─ content: str         ├─ messages: List[ChatMessage]
├─ sources: List        ├─ user_id: str
└─ timestamp: str       └─ created_at: str
```

### config.py (설정)
```
CommonConfig (최상위)
├─ environment: str          (dev, staging, prod)
├─ project_name: str
│
├─ data: DataConfig
│   ├─ data_dir: str
│   ├─ chunk_size: int
│   └─ vector_store_dir: str
│
├─ model: ModelConfig
│   ├─ embedding_model: str
│   ├─ llm_model: str
│   ├─ openai_api_key: str
│   └─ tavily_api_key: str
│
├─ pipeline: PipelineConfig
│   ├─ top_k: int
│   ├─ use_web_search: bool
│   └─ relevance_threshold: float
│
├─ ui: UIConfig
│   ├─ theme: str
│   └─ show_debug_info: bool
│
└─ logging: LoggingConfig
    ├─ level: str
    └─ log_file: str
```

## 📋 팀원별 작업 플로우

```
팀원 A (임베딩 모델)
  ├─ base.py: BaseEmbedding 참고
  ├─ extensions/embeddings/ 생성
  ├─ OpenAIEmbedding(BaseEmbedding) 구현
  └─ extensions/__init__.py에 등록

팀원 B (검색 알고리즘)
  ├─ base.py: BaseRetriever 참고
  ├─ extensions/retrievers/ 생성
  ├─ MMRRetriever(BaseRetriever) 구현
  └─ extensions/__init__.py에 등록

팀원 C (RAG 파이프라인 & 웹검색)
  ├─ base.py: BaseRAGPipeline 참고
  ├─ extensions/pipelines/ 생성
  ├─ CRAGPipeline(SimpleRAGPipeline) 구현
  ├─ BaseLLMClient, BaseWebSearch 구현
  └─ extensions/__init__.py에 등록

팀원 D (도메인 특화)
  ├─ pipelines.py: SimpleRAGPipeline 참고
  ├─ extensions/modules/ 생성
  ├─ MedicalRAG(SimpleRAGPipeline) 구현
  ├─ 도메인 특화 프롬프트 작성
  └─ extensions/__init__.py에 등록
```

## 🚀 실행 흐름

```
┌─ 사용자 질문 ─┐
│              │
├─ 설정 로드   │─ config.py
├─ 파이프라인  │─ pipelines.py (또는 확장된 파이프라인)
│   ├─ retrieve()  │─ 팀원 B의 retriever
│   ├─ grade()     │─ base.py의 기본 구현
│   ├─ generate()  │─ 팀원 C의 LLM 클라이언트
│   └─ process()   │─ 통합 처리
│
├─ 데이터 처리 │─ models.py
│   ├─ QueryRequest 생성
│   ├─ QueryResponse 생성
│   └─ SourceInfo 생성
│
├─ 유틸리티    │─ utils.py
│   ├─ 로깅
│   ├─ 캐싱
│   └─ 형식 변환
│
└─ 응답 반환 ──┘
```

## 💾 저장 구조

```
프로젝트 루트/
├── common/                  (공통 모듈 - 읽기 전용)
│   ├── base.py
│   ├── config.py
│   ├── models.py
│   ├── pipelines.py
│   ├── utils.py
│   └── extensions/          (팀원 작업 영역)
│
├── tests/                   (테스트 코드)
│   ├── test_base.py
│   ├── test_config.py
│   └── test_extensions.py
│
├── data/                    (데이터)
│   ├── raw/
│   ├── processed/
│   └── chroma_db/
│
├── logs/                    (로그)
│   └── app.log
│
└── requirements.txt         (의존성)
```

## 🔐 보호 정책

### ✅ 수정 가능
- `extensions/` 폴더: 팀원들이 자유롭게 작업
- 팀원의 구현 코드
- 테스트 코드

### ❌ 수정 불가 (보호)
- `base.py`: 인터페이스 보호
- `config.py`: 설정 구조 보호
- `models.py`: 데이터 구조 보호
- `pipelines.py`: 기본 파이프라인 보호

### ⚠️ 수정 필요시
프로젝트 리드와 협의 후 진행

## 📊 성능 고려사항

```
common/
├── base.py                  가벼움 (인터페이스만)
├── config.py               가벼움 (설정만)
├── models.py               가벼움 (데이터 구조)
├── pipelines.py            중간 (기본 처리 로직)
└── utils.py                중간 (유틸리티 함수들)

extensions/
├── embeddings/             무거움 (모델 로드)
├── retrievers/             중간 (검색 로직)
├── pipelines/              무거움 (고도화 로직)
└── modules/                무거움 (도메인 로직)

→ 필요시에만 import하여 최적화
```

## 🎓 학습 순서

```
1단계: 기초 이해 (1시간)
   └─ base.py, models.py 읽기

2단계: 설정 학습 (30분)
   └─ config.py 이해

3단계: 파이프라인 분석 (1시간)
   └─ pipelines.py 코드 분석

4단계: 유틸리티 활용 (30분)
   └─ utils.py 함수들 학습

5단계: 예시 실행 (1시간)
   └─ extensions/example_implementations.py 실행

6단계: 자신의 구현 시작
   └─ 선택한 영역에서 작업 시작
```

---

**다음 단계**: [COMMON_MODULE_GUIDE.md](./COMMON_MODULE_GUIDE.md)를 읽고 작업을 시작하세요! 🚀


