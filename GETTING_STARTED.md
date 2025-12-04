# 🎯 공통 모듈 시작하기

**작성일**: 2025년 12월 4일  
**상태**: ✅ 공통 모듈 구축 완료

---

## 🚀 5분 안에 시작하기

### Step 1️⃣: 공통 모듈 위치 확인
```bash
ls -la common/
# 출력:
# __init__.py
# base.py
# config.py
# models.py
# pipelines.py
# utils.py
# README.md
# STRUCTURE.md
# COMMON_MODULE_GUIDE.md
# extensions/
```

### Step 2️⃣: 문서 읽기 순서
```
1. 지금 이 파일 (5분)
   ↓
2. common/README.md (10분)
   ↓
3. common/STRUCTURE.md (10분)
   ↓
4. common/COMMON_MODULE_GUIDE.md (30분)
   ↓
5. 자신의 담당 영역에 해당하는 구현 시작
```

### Step 3️⃣: 예시 코드 실행
```bash
python common/extensions/example_implementations.py
```

---

## 📌 공통 모듈이란?

### 정의
**공통 모듈**은 모든 팀원이 사용할 **기준이 되는 RAG 시스템의 뼈대**입니다.

### 목적
- ✅ 모든 팀원이 따를 명확한 인터페이스 제공
- ✅ 팀원 간 독립적 작업 가능
- ✅ 쉬운 통합 (플러그인 방식)
- ✅ 확장 가능한 아키텍처

### 구조
```
공통 모듈 (모든 팀원 사용)
├─ base.py: 인터페이스 정의
├─ config.py: 설정
├─ models.py: 데이터 구조
├─ pipelines.py: 기본 구현
└─ utils.py: 유틸리티

     ↓↓↓ 각 팀원이 여기서 고도화 ↓↓↓

확장 모듈 (팀원별 작업)
├─ extensions/embeddings/ (팀원 A)
├─ extensions/retrievers/ (팀원 B)
├─ extensions/pipelines/ (팀원 C)
└─ extensions/modules/ (팀원 D)
```

---

## 👥 팀원별 역할

### 팀원 A: 임베딩 모델 최적화
**위치**: `common/extensions/embeddings/`

- OpenAI, HuggingFace, 로컬 LLM 등 다양한 임베딩 모델 구현
- 성능 최적화 (배치 처리, 캐싱)
- 다국어 지원

### 팀원 B: 검색 알고리즘 개선
**위치**: `common/extensions/retrievers/`

- MMR (Maximum Marginal Relevance) 검색
- BM25 검색
- 하이브리드 검색
- 벡터 저장소 (Chroma, Pinecone 등)

### 팀원 C: RAG 파이프라인 고도화
**위치**: `common/extensions/pipelines/`, `llm_clients/`, `web_search/`

- CRAG (Corrective RAG) 구현
- 웹 검색 통합
- 답변 품질 검사
- 비용 최적화

### 팀원 D: 도메인 특화 모듈
**위치**: `common/extensions/modules/`

- 의료 도메인 RAG
- 법률 도메인 RAG
- 금융 도메인 RAG
- 도메인별 프롬프트 튜닝

---

## 📁 주요 파일 설명

### base.py ⭐⭐⭐ (가장 중요!)
모든 구현이 상속해야 할 인터페이스를 정의합니다.

```python
# 임베딩 모델
class BaseEmbedding(ABC):
    def embed_text(text: str) -> List[float]: pass
    def embed_batch(texts: List[str]) -> List[List[float]]: pass

# 검색기
class BaseRetriever(ABC):
    def retrieve(query: str, top_k: int) -> List[RetrievalResult]: pass

# RAG 파이프라인
class BaseRAGPipeline(ABC):
    def retrieve(query: str, top_k: int) -> List[RetrievalResult]: pass
    def grade(query: str, documents) -> Tuple[List[bool], Dict]: pass
    def generate(query: str, documents) -> str: pass
    def process(query: str, **kwargs) -> Dict: pass
```

### config.py
설정을 중앙에서 관리합니다.

```python
config = CommonConfig(
    model=ModelConfig(
        llm_model="gpt-4o-mini",
        embedding_model="text-embedding-3-small",
    ),
    pipeline=PipelineConfig(
        top_k=5,
        use_web_search=True,
    )
)
```

### models.py
타입 안전성을 보장하는 데이터 모델입니다.

```python
QueryRequest → Pipeline → QueryResponse
    ↓
  (제목, 내용)    ↓    (답변, 출처, 메트릭)
              SimpleRAGPipeline
```

### pipelines.py
최소한의 작동하는 기본 구현입니다.

```python
pipeline = SimpleRAGPipeline(...)
response = pipeline.process("사용자 질문")
```

### utils.py
공통 유틸리티 함수입니다.

```python
- setup_logging(): 로깅 설정
- load_json(), save_json(): 파일 I/O
- chunk_text(): 텍스트 청킹
- cache_result: 캐싱 데코레이터
- 등 30+ 함수
```

---

## 📖 문서 가이드

### common/README.md
- 공통 모듈 소개
- 빠른 시작 가이드
- 코드 예시
- FAQ

### common/STRUCTURE.md
- 디렉토리 트리
- 의존성 관계도
- 각 파일의 역할
- 사용 흐름

### common/COMMON_MODULE_GUIDE.md ⭐⭐
- 팀원별 구현 패턴
- 설정 방법
- 데이터 흐름
- 모범 사례
- 협업 규칙

### common/extensions/README.md ⭐⭐
- 확장 모듈 구조
- 팀원별 담당 영역
- 구현 가이드
- 체크리스트

### common/extensions/example_implementations.py ⭐
- 각 컴포넌트의 구현 예시
- 테스트 코드
- 사용 방법

---

## ⚡ 빠른 참조

### 핵심 클래스
```python
from common.base import BaseRetriever, BaseRAGPipeline
from common.config import CommonConfig
from common.models import QueryRequest, QueryResponse
from common.pipelines import SimpleRAGPipeline
from common.utils import setup_logging
```

### 설정 로드
```python
from common.config import CommonConfig, get_config

# 기본 설정
config = CommonConfig()

# 환경별 설정
config = get_config("dev")    # 개발
config = get_config("prod")   # 프로덕션
```

### 로깅 설정
```python
from common.utils import setup_logging

logger = setup_logging()
logger.info("정보")
logger.warning("경고")
logger.error("오류")
```

### 파이프라인 실행
```python
from common.pipelines import SimpleRAGPipeline

pipeline = SimpleRAGPipeline(...)
response = pipeline.process("질문")

print(response['answer'])          # 답변
print(response['sources'])         # 출처
print(response['metrics'])         # 메트릭
```

---

## 🎯 다음 단계

### 1️⃣ 오늘 해야 할 일
- [ ] 이 파일 읽기 (5분)
- [ ] `common/README.md` 읽기 (10분)
- [ ] `common/STRUCTURE.md` 읽기 (10분)
- [ ] 담당 영역 결정 (5분)

### 2️⃣ 내일 해야 할 일
- [ ] `common/COMMON_MODULE_GUIDE.md` 정독 (30분)
- [ ] `common/base.py` 코드 분석 (30분)
- [ ] `common/extensions/README.md` 읽기 (20분)
- [ ] 예시 코드 실행 (30분)

### 3️⃣ 이번 주 해야 할 일
- [ ] 첫 번째 구현 완료 (팀원별로 상이)
- [ ] 테스트 코드 작성 (2시간)
- [ ] 통합 테스트 (1시간)
- [ ] PR 제출

---

## 🔑 핵심 개념 3가지

### 1️⃣ 인터페이스 기반 설계
모든 구현이 `BaseXXX`를 상속하여 같은 계약을 따릅니다.

```python
class MyEmbedding(BaseEmbedding):  # ← base.py에서 상속
    def embed_text(self, text: str) -> List[float]:
        # 구현
        pass
```

### 2️⃣ 플러그인 아키텍처
새로운 구현을 `extensions/`에서 추가하고 교체 가능합니다.

```python
# 기본 구현
from common.pipelines import SimpleRAGPipeline

# 팀원의 고도화 구현
from extensions.pipelines.crag import CRAGPipeline

# 원하는 구현 선택
pipeline = CRAGPipeline(...)
```

### 3️⃣ 공통 계약
모든 입출력이 동일한 형식을 따릅니다.

```python
# 입력: QueryRequest
request = QueryRequest(query="질문", top_k=5)

# 처리: 어떤 파이프라인이든
response = pipeline.process(request.query)

# 출력: QueryResponse
# {
#     'answer': '답변',
#     'sources': [...],
#     'metrics': {...}
# }
```

---

## ❓ 자주 묻는 질문

### Q1: 공통 모듈을 수정할 수 있나요?
**A**: 아니오. 공통 모듈은 모든 팀원의 기준입니다. 수정이 필요하면 프로젝트 리드와 상담하세요.

### Q2: 자신의 구현을 어디에 저장하나요?
**A**: `common/extensions/` 폴더의 해당 영역에 저장하세요.

### Q3: 다른 팀원의 구현을 사용할 수 있나요?
**A**: 네! 각자 `extensions/__init__.py`에 등록하면 모두가 사용 가능합니다.

### Q4: 어디서 시작해야 하나요?
**A**: 
1. `common/README.md` 읽기
2. 담당 영역 결정
3. `common/extensions/README.md` 읽기
4. 구현 시작

### Q5: 성능을 측정할 수 있나요?
**A**: 네! 모든 응답에 `metrics` 정보가 포함됩니다.

---

## 📞 도움말

### 문제가 발생했을 때
1. `common/COMMON_MODULE_GUIDE.md`의 FAQ 확인
2. `common/extensions/README.md`의 체크리스트 확인
3. 팀원들과 상담
4. 프로젝트 리드에 이슈 보고

### 더 알고 싶을 때
- 📖 `common/README.md`: 개요 및 빠른 시작
- 🏗️ `common/STRUCTURE.md`: 구조 설명
- 📚 `common/COMMON_MODULE_GUIDE.md`: 상세 가이드
- 🔧 `common/extensions/README.md`: 확장 가이드
- 💻 `common/extensions/example_implementations.py`: 예시 코드

---

## ✅ 준비 체크리스트

### 이 문서를 읽은 후
- [ ] 공통 모듈이 무엇인지 이해함
- [ ] 자신의 담당 영역을 알고 있음
- [ ] 다음에 읽을 문서를 알고 있음

### common/README.md를 읽은 후
- [ ] 공통 모듈의 구조를 이해함
- [ ] 빠른 시작 방법을 알고 있음
- [ ] 팀원별 역할을 이해함

### common/STRUCTURE.md를 읽은 후
- [ ] 전체 디렉토리 구조를 이해함
- [ ] 각 파일의 역할을 알고 있음
- [ ] 의존성 관계도를 이해함

### 구현을 시작하기 전
- [ ] `common/base.py`의 인터페이스를 이해함
- [ ] `common/extensions/README.md`를 읽음
- [ ] 예시 코드(`example_implementations.py`)를 실행함
- [ ] 구현 패턴을 결정함

---

## 🚀 시작하기

### 지금 바로 할 수 있는 것들

**3분 내에**:
```bash
# 공통 모듈 위치 확인
ls common/
```

**10분 내에**:
```bash
# common/README.md 읽기
cat common/README.md
```

**30분 내에**:
```bash
# 예시 코드 실행
python common/extensions/example_implementations.py
```

**1시간 내에**:
```bash
# 자신의 담당 영역 결정
# common/extensions/README.md 읽기
# 첫 번째 파일 생성
```

---

## 🎓 학습 경로 (3시간)

```
1단계: 기초 이해 (30분)
├─ GETTING_STARTED.md (이 파일)
├─ common/README.md
└─ common/STRUCTURE.md

2단계: 코드 분석 (60분)
├─ common/base.py
├─ common/config.py
├─ common/models.py
└─ common/pipelines.py

3단계: 예시 실행 (30분)
└─ common/extensions/example_implementations.py

4단계: 구현 가이드 (30분)
├─ common/COMMON_MODULE_GUIDE.md
└─ common/extensions/README.md

5단계: 자신의 구현 시작
└─ extensions/[영역]/
```

---

## 💡 팁

### 코드를 읽을 때
1. 전체 구조를 먼저 파악하세요
2. 세부 구현은 나중에 이해해도 괜찮습니다
3. 예시 코드로 실행 흐름을 확인하세요

### 구현할 때
1. `BaseXXX` 클래스를 먼저 확인하세요
2. `example_implementations.py`의 예시를 참고하세요
3. 로깅과 에러 처리를 추가하세요
4. 타입 힌팅과 docstring을 작성하세요

### 팀원과 협업할 때
1. 먼저 `extensions/__init__.py`를 수정하지 마세요
2. 자신의 구현이 완료된 후 등록하세요
3. 인터페이스를 변경하지 마세요 (다른 팀원 영향)
4. PR로 코드를 공유하세요

---

## 🎉 마지막 말씀

축하합니다! 🎊

이제 **공통 기준이 되는 모듈**이 준비되었습니다.  
각 팀원이 이를 기반으로 **자신의 영역을 고도화**할 수 있습니다.

> **핵심**: 공통 모듈은 모두를 위한 **기준**이며, **확장**을 위한 **기반**입니다.

**지금 바로 시작하세요!** 🚀

---

## 📚 다음 읽을 문서

1. **지금 읽는 중**: GETTING_STARTED.md (이 파일)
2. **다음**: `common/README.md`
3. **그 다음**: `common/STRUCTURE.md`
4. **그 다음**: `common/COMMON_MODULE_GUIDE.md`

---

**행운을 빕니다!** 💻✨


