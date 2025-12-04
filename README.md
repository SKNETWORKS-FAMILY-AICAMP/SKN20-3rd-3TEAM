# 🐾 반려동물 의료 RAG 기반 멀티채널 LLM 서비스

반려동물 전문 의료 QA 및 동물병원 위치 안내를 제공하는 **Retrieval-Augmented Generation (RAG)** 기반 멀티채널 LLM 서비스입니다.

## 📋 목차

- [개요](#개요)
- [주요 기능](#주요-기능)
- [시스템 아키텍처](#시스템-아키텍처)
- [빠른 시작](#빠른-시작)
- [프로젝트 구조](#프로젝트-구조)
- [핵심 모듈](#핵심-모듈)
- [확장 가이드](#확장-가이드)
- [테스트](#테스트)

---

## 개요

이 프로젝트는 **공통 기준 코드(Foundation)**로 설계되었으며, 모든 팀원이 각자의 역할에 맞춰 확장하고 고도화할 수 있는 구조를 제공합니다.

### 주요 특징

✅ **모듈식 아키텍처**: 각 모듈이 독립적으로 개발/테스트 가능  
✅ **LangGraph 기반**: CRAG(Corrective RAG) 파이프라인 구현  
✅ **다중 검색 전략**: 벡터 검색 + 웹 검색 폴백 메커니즘  
✅ **의도 기반 라우팅**: 질문 분류에 따른 최적 처리 경로  
✅ **Streamlit UI**: 즉시 실행 가능한 웹 인터페이스  

---

## 주요 기능

### 1️⃣ 의도 분류 (Intent Classification)
- **QuestionClassifier**: 사용자 질문을 4가지 카테고리로 분류
  - `medical`: 의료/건강 관련
  - `hospital`: 병원 정보/위치
  - `general`: 일반 정보
  - `unknown`: 미분류

### 2️⃣ 벡터 검색 시스템
- **VectorStoreRetriever**: ChromaDB 기반 임베딩 검색
- 의료 문서 데이터베이스에서 관련성 높은 문서 검색

### 3️⃣ 웹 검색 시스템
- **HospitalWebSearcher**: 병원 정보 및 위치 검색
- **GeneralWebSearcher**: 일반 정보 및 백업 검색

### 4️⃣ 병원 위치 매핑
- **HospitalMapper**: 지역 텍스트 → 좌표 변환
- 카카오맵 API 기반 병원 정보 통합

### 5️⃣ CRAG 파이프라인
- **LangGraphRAGPipeline**: 4단계 워크플로우
  1. 벡터 검색
  2. 관련성 판단
  3. 웹 검색 (필요시)
  4. 답변 생성

### 6️⃣ 오케스트레이션
- **QueryOrchestrator**: 전체 시스템 조율
- 의도 분류 → 적절한 처리 경로 선택

---

## 시스템 아키텍처

```
┌─────────────────────────────────────────────────────────────┐
│                      Streamlit UI                           │
│                     (app.py)                                │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│           QueryOrchestrator                                 │
│     (src/orchestrator/query_orchestrator.py)               │
└────┬──────────┬──────────────┬──────────────┬───────────────┘
     │          │              │              │
     ▼          ▼              ▼              ▼
┌─────────┐ ┌────────┐ ┌──────────┐ ┌─────────────┐
│Classifier│ │  RAG   │ │ Hospital │ │General Web  │
│          │ │Pipeline│ │ Mapper   │ │ Searcher    │
└─────────┘ └────────┘ └──────────┘ └─────────────┘
     │          │              │              │
     │          ▼              │              │
     │    ┌──────────────────────────┐       │
     │    │  LangGraph Nodes:        │       │
     │    │ - Retrieval              │       │
     │    │ - Relevance Evaluation   │       │
     │    │ - Web Search Fallback    │       │
     │    │ - Generation             │       │
     │    └──────────────────────────┘       │
     │          │                            │
     ▼          ▼                            ▼
┌─────────────────────────────────────────────────┐
│          External Services                      │
│  - ChromaDB (Vector Store)                      │
│  - OpenAI Embedding API                         │
│  - Google/Naver Search API                      │
│  - Kakao Map API                                │
└─────────────────────────────────────────────────┘
```

---

## 빠른 시작

### 설치

```bash
# 1. 저장소 클론
git clone <repository-url>
cd pet-medical-rag

# 2. 가상 환경 생성 (Python 3.10+)
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

# 3. 의존성 설치
pip install -r requirements.txt

# 4. 환경 변수 설정
cp .env.example .env
# .env 파일을 열어 실제 API 키를 입력하세요
```

### 실행

```bash
# Streamlit 앱 실행
streamlit run app.py

# 브라우저에서 http://localhost:8501 접속
```

### 기본 테스트

```bash
# Python 대화형 셸에서 테스트
python

>>> from src.orchestrator.query_orchestrator import QueryOrchestrator
>>> orchestrator = QueryOrchestrator()
>>> 
>>> # 의료 질문
>>> result = orchestrator.process("우리 강아지가 피부염이 있는데 어떻게 하죠?")
>>> print(result["data"].answer)
>>>
>>> # 병원 질문
>>> result = orchestrator.process("강남역 근처 동물병원 찾아줄래?")
>>> print(result["data"].hospitals)
```

---

## 프로젝트 구조

```
pet_medical_rag/
├── app.py                          # Streamlit UI 메인 진입점
├── requirements.txt                # 패키지 의존성
│
├── src/
│   ├── config/
│   │   ├── settings.py            # 환경 변수 및 전역 설정
│   │   └── logger.py              # 공통 로깅
│   │
│   ├── types/
│   │   ├── document.py            # Document 타입 정의
│   │   ├── query.py               # Query & Classification 타입
│   │   └── response.py            # Response 타입
│   │
│   ├── utils/
│   │   └── helpers.py             # 공통 헬퍼 함수
│   │
│   ├── classifier/
│   │   └── question_classifier.py # 의도 분류 (QuestionClassifier)
│   │
│   ├── retriever/
│   │   └── vector_store_retriever.py # 벡터 검색 (VectorStoreRetriever)
│   │
│   ├── web/
│   │   ├── hospital_web_searcher.py  # 병원 검색 (HospitalWebSearcher)
│   │   └── general_web_searcher.py   # 일반 검색 (GeneralWebSearcher)
│   │
│   ├── mapping/
│   │   └── hospital_mapper.py     # 병원 위치 매핑 (HospitalMapper)
│   │
│   ├── rag/
│   │   ├── langgraph_crag_pipeline.py # CRAG 파이프라인 메인
│   │   ├── graph_builder.py           # 그래프 구성
│   │   └── nodes/
│   │       ├── retrieval_node.py      # 검색 노드
│   │       ├── relevance_node.py      # 관련성 판단 노드
│   │       ├── web_search_node.py     # 웹 검색 노드
│   │       └── generation_node.py     # 답변 생성 노드
│   │
│   └── orchestrator/
│       └── query_orchestrator.py  # 전체 시스템 오케스트레이션
│
├── tests/
│   ├── test_classifier.py
│   ├── test_retriever.py
│   ├── test_pipeline.py
│   └── test_integration.py
│
├── data/
│   ├── docs/                      # 의료 문서 저장소
│   ├── chroma_db/                 # 벡터 DB 저장 경로
│   └── mock_data.json             # 테스트용 Mock 데이터
│
├── README.md                      # 이 파일
├── ARCHITECTURE.md                # 상세 아키텍처 설명
├── CONTRIBUTION.md                # 팀원 확장 가이드
└── PROJECT_STRUCTURE.txt          # 프로젝트 구조 상세 설명
```

---

## 핵심 모듈

### 1. QuestionClassifier
```python
from src.classifier.question_classifier import QuestionClassifier

classifier = QuestionClassifier()
result = classifier.classify("우리 강아지가 피부염이...")
print(result.intent)  # "medical"
print(result.confidence)  # 0.95
```

**확장 포인트**:
- LLM 기반 분류로 업그레이드 (`classify_with_llm()`)
- 새로운 의도 카테고리 추가
- 커스텀 키워드 추가 (`add_custom_keywords()`)

### 2. VectorStoreRetriever
```python
from src.retriever.vector_store_retriever import VectorStoreRetriever

retriever = VectorStoreRetriever()
results = retriever.search("반려견 피부염 증상", top_k=5)

for doc in results.documents:
    print(f"Score: {doc.score}")
    print(f"Content: {doc.content[:100]}...")
```

**확장 포인트**:
- ChromaDB 실제 연동
- 다른 벡터DB 지원 (Pinecone, Weaviate 등)
- 임베딩 모델 변경

### 3. LangGraphRAGPipeline
```python
from src.rag.langgraph_crag_pipeline import LangGraphRAGPipeline

pipeline = LangGraphRAGPipeline()
response = pipeline.invoke(
    query="반려견 피부염 치료법",
    intent="medical"
)
print(response.answer)
print(response.documents)
```

**확장 포인트**:
- LLM 기반 답변 생성 (`generation_node_llm()`)
- 새로운 노드 추가
- 스트리밍 지원

### 4. QueryOrchestrator
```python
from src.orchestrator.query_orchestrator import QueryOrchestrator

orchestrator = QueryOrchestrator()
result = orchestrator.process("우리 강아지 병원 찾아줄래?")

if result["type"] == "hospital":
    hospitals = result["data"].hospitals
    for h in hospitals:
        print(f"{h['name']} - {h['distance']}m away")
```

---

## 확장 가이드

### 팀원 역할별 확장 방향

#### 🔍 **데이터/검색 팀**
- `src/retriever/`: ChromaDB 실제 연동, 더 나은 검색 알고리즘
- `src/web/`: 실제 API (Google, Naver, Kakao) 연동
- 의료 문서 수집 및 벡터화

#### 🧠 **LLM/AI 팀**
- `src/classifier/question_classifier.py`: LLM 기반 분류기로 확장
- `src/rag/nodes/generation_node.py`: GPT-4/Claude 기반 답변 생성
- `src/rag/nodes/relevance_node.py`: LLM 기반 관련성 평가

#### 🏥 **도메인/비즈니스 팀**
- `src/mapping/hospital_mapper.py`: 병원 정보 DB 구축
- 도메인 특화 규칙 추가
- 사용자 피드백 루프 구현

#### 🎨 **프론트엔드 팀**
- `app.py`: Streamlit UI 개선
- 고급 시각화
- 모바일 앱 개발

---

## 테스트

### 단위 테스트
```bash
# 분류기 테스트
pytest tests/test_classifier.py -v

# 검색 시스템 테스트
pytest tests/test_retriever.py -v

# RAG 파이프라인 테스트
pytest tests/test_pipeline.py -v
```

### 통합 테스트
```bash
# 전체 시스템 테스트
pytest tests/test_integration.py -v

# 특정 테스트만 실행
pytest tests/test_integration.py::test_end_to_end -v
```

### 수동 테스트
```python
# Python 대화형 셸에서 테스트
python

>>> from src.orchestrator.query_orchestrator import QueryOrchestrator
>>> from src.classifier.question_classifier import QuestionClassifier
>>>
>>> # 분류기 테스트
>>> clf = QuestionClassifier()
>>> print(clf.classify("우리 강아지 피부염이...").intent)
>>>
>>> # 오케스트레이터 테스트
>>> orch = QueryOrchestrator()
>>> result = orch.process("강남역 근처 동물병원")
>>> print(result["type"])
```

---

## 환경 변수 설정

`.env` 파일을 생성하고 다음 변수들을 설정하세요:

```env
# LLM 설정
OPENAI_API_KEY=sk-...
LLM_MODEL=gpt-4

# 벡터 DB
CHROMA_PERSIST_DIR=./data/chroma_db
EMBEDDING_MODEL=text-embedding-ada-002

# 웹 검색 API
GOOGLE_SEARCH_API_KEY=...
KAKAO_MAP_API_KEY=...

# 시스템
LOG_LEVEL=INFO
DEBUG=false
```

---

## 주요 클래스 및 메서드

| 클래스 | 메서드 | 설명 |
|--------|--------|------|
| `QuestionClassifier` | `classify(query)` | 질문 분류 |
| | `classify_with_llm(query)` | LLM 기반 분류 |
| | `add_custom_keywords()` | 키워드 추가 |
| `VectorStoreRetriever` | `search(query, top_k)` | 벡터 검색 |
| | `add_documents(docs)` | 문서 추가 |
| | `health_check()` | 상태 확인 |
| `HospitalWebSearcher` | `search(query)` | 병원 검색 |
| | `search_by_coordinates()` | 좌표 기반 검색 |
| | `get_hospital_details()` | 병원 상세정보 |
| `HospitalMapper` | `extract_and_search()` | 위치 추출 및 검색 |
| | `extract_location()` | 위치 정보 추출 |
| | `get_distance()` | 거리 계산 |
| `LangGraphRAGPipeline` | `invoke(query, intent)` | 파이프라인 실행 |
| | `invoke_batch(queries)` | 배치 처리 |
| | `health_check()` | 시스템 상태 확인 |
| `QueryOrchestrator` | `process(query)` | 전체 시스템 실행 |
| | `get_statistics()` | 통계 조회 |

---

## 로깅 및 디버깅

### 로그 레벨 설정
```python
from src.config.settings import settings

settings.LOG_LEVEL = "DEBUG"  # DEBUG, INFO, WARNING, ERROR
settings.DEBUG = True
```

### 로거 사용
```python
from src.config.logger import get_logger

logger = get_logger(__name__)
logger.info("Information message")
logger.debug("Debug message")
logger.error("Error message")
```

---

## 성능 최적화 팁

1. **벡터 검색 최적화**
   - ChromaDB 색인 크기 조정
   - 배치 검색 활용

2. **LLM 호출 최적화**
   - 결과 캐싱
   - 토큰 사용량 모니터링
   - 동적 프롬프트 길이 조정

3. **웹 검색 최적화**
   - 결과 캐싱
   - 요청 타임아웃 설정
   - Rate limiting

---

## 기여 가이드

팀원들의 기여를 환영합니다!

1. **Feature Branch 생성**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **코드 작성 및 테스트**
   ```bash
   pytest tests/
   ```

3. **Pull Request 제출**
   - 상세한 설명 포함
   - 관련 이슈 링크

더 자세한 내용은 [CONTRIBUTION.md](CONTRIBUTION.md) 참조

---

## 라이선스

MIT License - 자유롭게 사용, 수정, 배포 가능

---

## 연락처

- 프로젝트 리드: [팀 리더 이름]
- 이메일: [이메일]
- 슬랙: #pet-medical-rag

---

## 버전 히스토리

- **v0.1.0** (2024-01-15)
  - 초기 프로젝트 구조
  - 핵심 모듈 구현
  - Streamlit UI 기본 버전

---

**Happy Coding! 🐾**

