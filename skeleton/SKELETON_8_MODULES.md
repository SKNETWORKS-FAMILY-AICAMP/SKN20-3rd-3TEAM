# 🎯 RAG 어시스턴트 스켈레톤 코드 - 8개 핵심 모듈 완성

**작성일**: 2025-12-05  
**프로젝트**: RAG 기반 AI 어시스턴트 (최소 기초 스켈레톤)  
**상태**: ✅ 완성 (8개 모듈)

---

## 📋 개요

기존의 복잡한 RAG 시스템을 **8개의 핵심 모듈**로 최소화하여 단순하고 명확한 스켈레톤 코드를 작성했습니다.

### 요청사항 충족 확인

| 항목 | 요청사항 | 완성도 |
|------|---------|--------|
| 모듈 개수 | **8개** 핵심 모듈 | ✅ 완료 |
| 코드 형식 | 함수/클래스 시그니처 + 주석 | ✅ 완료 |
| 구현 | 실제 로직 제거, TODO 주석 | ✅ 완료 |
| 반환값 | 더미 데이터 반환 | ✅ 완료 |
| 문서화 | 상세 Docstring | ✅ 완료 |
| 테스트 | 각 모듈 테스트 코드 | ✅ 완료 |

---

## 📦 8개 핵심 모듈

### 1️⃣ **data_processor.py** (문서 전처리 및 청킹)

**파일 크기**: ~200줄  
**주요 함수**:
- `preprocess_document(file_path: str) -> List[str]`
- `clean_text(text: str) -> str`
- `chunk_text(text: str, chunk_size: int, overlap: int) -> List[str]`
- `extract_metadata(file_path: str, text: str) -> Dict[str, str]`
- `batch_preprocess_documents(file_paths: List[str]) -> List[Dict]`

**책임**:
- 다양한 형식 문서 로드 (JSON, TXT, PDF)
- 텍스트 정규화 및 정제
- 의미 있는 단위로 문서 청킹
- 메타데이터 추출 관리

**워크플로우**:
```
파일 로드 → 텍스트 추출 → 정제 → 청킹 → 메타데이터 추출 → 청크 리스트 반환
```

---

### 2️⃣ **vector_store_manager.py** (임베딩 및 벡터 DB 관리)

**파일 크기**: ~250줄  
**주요 클래스/함수**:
- `VectorStoreManager` 클래스
- `embed_chunk(text: str) -> List[float]`
- `embed_and_index_chunks(chunks: List[str]) -> bool`
- `search_similar_chunks(query: str, top_k: int) -> List[Tuple]`
- `delete_chunk_by_id(chunk_id: str) -> bool`
- `get_stats() -> Dict`

**책임**:
- 임베딩 모델 초기화 및 관리
- 텍스트 → 벡터 변환
- 벡터 DB (Chroma) 저장
- 유사도 검색
- DB 생명주기 관리

**워크플로우**:
```
청크 텍스트 → 임베딩 생성 → ID 할당 → 메타데이터 추가 → DB 저장
```

---

### 3️⃣ **input_classifier.py** (사용자 의도 분류)

**파일 크기**: ~100줄  
**주요 함수**:
- `classify_query(query: str) -> str`
- `classify_query_with_confidence(query: str) -> Tuple[str, float]`
- `get_classification_keywords() -> dict`

**책임**:
- 사용자 쿼리 분석
- 3가지 분류 중 하나로 분류
- 분류 신뢰도 계산

**분류 카테고리**:
- `"medical_consultation"`: 의료 상담 (증상, 질병, 치료)
- `"map_search"`: 지도 검색 (병원, 위치)
- `"general"`: 일반 질문 (기타)

---

### 4️⃣ **rag_handler.py** (RAG 및 웹 검색)

**파일 크기**: ~150줄  
**주요 함수**:
- `perform_rag_search(query: str) -> str`
- `perform_web_search(query: str) -> str`
- `search_with_fallback(query: str) -> Tuple[str, str]`
- `grade_documents(query: str, documents: list) -> list`
- `format_context(documents: list) -> str`

**책임**:
- 벡터 DB를 활용한 RAG 검색
- 웹 검색 API 통합
- CRAG 패턴 구현 (폴백)
- 문서 관련성 평가

**CRAG 패턴**:
```
쿼리 → RAG 검색 → 관련 문서 충분? → YES: 반환
                          ↓
                         NO: 웹 검색 → 반환
```

---

### 5️⃣ **map_handler.py** (지도/API 처리)

**파일 크기**: ~180줄  
**주요 함수**:
- `get_map_info(query: str) -> str`
- `extract_hospital_name(query: str) -> Optional[str]`
- `extract_location(query: str) -> Optional[str]`
- `format_map_response(hospitals: List[Dict]) -> str`
- `calculate_distance(lat1, lon1, lat2, lon2) -> float`
- `get_hospital_by_name(name: str) -> Optional[Dict]`

**책임**:
- 쿼리에서 병원명/위치 추출
- 지도 API (카카오맵) 호출
- 거리 기반 정렬
- 사용자 친화적 포맷팅

**처리 순서**:
```
쿼리 → 위치/병원명 추출 → API 호출 → 거리 계산 → 정렬 → 포맷팅 → 반환
```

---

### 6️⃣ **llm_generator.py** (LLM 응답 생성)

**파일 크기**: ~250줄  
**주요 함수**:
- `build_system_prompt(query_type: str) -> str`
- `generate_response(query: str, context: str) -> str`
- `rewrite_response(response: str, feedback: str) -> str`
- `estimate_token_count(text: str) -> int`
- `truncate_context(context: str, max_length: int) -> str`
- `calculate_token_cost(input_tokens, output_tokens) -> float`

**책임**:
- 쿼리 타입별 프롬프트 엔지니어링
- OpenAI GPT API 호출
- 피드백 기반 응답 재작성
- 토큰 관리 및 최적화

**프롬프트 유형**:
- Medical: 수의학 전문가 역할
- Map: 지역 정보 전문가 역할
- General: 일반 AI 어시스턴트

---

### 7️⃣ **evaluation_controller.py** (응답 평가 및 흐름 제어)

**파일 크기**: ~250줄  
**주요 함수**:
- `evaluate_response(response: str) -> Dict`
- `check_accuracy(response: str) -> float`
- `check_clarity(response: str) -> float`
- `check_completeness(response: str) -> float`
- `check_safety_guidelines(response: str) -> Dict`
- `determine_next_action(response: str, evaluation: Dict) -> Literal`
- `generate_feedback(scores: Dict, response: str) -> str`
- `collect_evaluation_metrics(...) -> Dict`

**책임**:
- 4개 차원 응답 품질 평가
- 평가 결과 기반 다음 액션 결정
- 개선 피드백 생성
- 메트릭 수집 및 로깅

**평가 차원**:
- 정확도 (Accuracy)
- 명확성 (Clarity)
- 완전성 (Completeness)
- 안전성 (Safety)

**의사결정 기준**:
```
점수 >= 0.75      → ✅ ACCEPT (응답 승인)
0.50 <= 점수 < 0.75 → 🔄 REWRITE (재작성, 최대 2회)
점수 < 0.50       → ⚠️ ESCALATE (수동 개입)
```

---

### 8️⃣ **main.py** (전체 워크플로우 오케스트레이션)

**파일 크기**: ~350줄  
**주요 함수**:
- `indexing_workflow(file_paths: List[str]) -> bool`
- `main_workflow(query: str, max_rewrite_attempts: int) -> str`
- `main_workflow_with_feedback(query: str, feedback: str) -> str`
- `batch_workflow(queries: List[str]) -> List[Dict]`

**책임**:
- 7개 모듈 통합 오케스트레이션
- 엔드-투-엔드 쿼리 처리
- 색인 구축 워크플로우 관리
- 배치 처리 지원

**3가지 워크플로우**:

1. **indexing_workflow**: 문서 색인 구축
   ```
   파일들 → 전처리 → 청킹 → 임베딩 → DB 저장
   ```

2. **main_workflow**: 단일 쿼리 처리
   ```
   쿼리 → 분류 → 검색 → 프롬프트 → LLM → 평가 → (재작성?) → 반환
   ```

3. **batch_workflow**: 배치 처리
   ```
   여러 쿼리 → [main_workflow 반복] → 통계 반환
   ```

---

## 🔄 통합 워크플로우

### 전체 처리 흐름

```
┌─────────────────────────────────────────────────────────────┐
│                      사용자 입력                              │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
                ┌──────────────────────────┐
                │ [1] INPUT CLASSIFIER     │
                │   의도 분류              │
                └───────────┬──────────────┘
                            │
            ┌───────────────┼───────────────┐
            │               │               │
            ▼               ▼               ▼
      Medical          Map Search        General
     (RAG 검색)      (지도 API)        (웹 검색)
            │               │               │
            └───────────────┼───────────────┘
                            │
                            ▼
        ┌─────────────────────────────────┐
        │ [2] RAG/MAP/WEB HANDLER          │
        │   정보 검색                     │
        └────────────┬────────────────────┘
                     │
                     ▼
        ┌─────────────────────────────────┐
        │ [3] LLM GENERATOR               │
        │   응답 생성                     │
        └────────────┬────────────────────┘
                     │
                     ▼
        ┌─────────────────────────────────┐
        │ [4] EVALUATION CONTROLLER       │
        │   응답 평가                     │
        │   (4개 차원, 점수 계산)         │
        └────────────┬────────────────────┘
                     │
            ┌────────┴────────┐
            │                 │
          PASS?           REWRITE?
            │                 │
           YES              YES
            │       (최대 2회)
            │                 │
            └────────┬────────┘
                     │
                     ▼
    ┌───────────────────────────────┐
    │ ✨ 최종 답변 반환             │
    │ + 메트릭 수집                 │
    └───────────────────────────────┘
```

### 8개 모듈 간 의존성

```
                     main.py
                  (오케스트레이션)
                        │
        ┌───────────────┼───────────────┬──────────────┐
        │               │               │              │
        ▼               ▼               ▼              ▼
    data_         vector_          input_          rag_
    processor     manager          classifier      handler
                      ▲                 │              │
                      │                 │              │
                      └─────────────────┼──────────────┘
                                        │
                      ┌─────────────────┼──────────────┐
                      │                 │              │
                      ▼                 ▼              ▼
                  map_            llm_            evaluation_
                  handler         generator       controller
```

---

## 📊 코드 통계

| 항목 | 수치 |
|------|------|
| **총 Python 파일** | 8개 |
| **총 라인 수** | ~1,500줄 |
| **평균 파일 크기** | 188줄 |
| **함수/클래스 개수** | 35+개 |
| **TODO 주석** | 각 함수에 명확히 표시 |
| **더미 반환값** | 모든 함수 포함 |

### 파일별 상세

| 파일명 | 라인 수 | 함수 개수 | 설명 |
|--------|--------|---------|------|
| `data_processor.py` | ~200 | 5 | 문서 전처리 |
| `vector_store_manager.py` | ~250 | 1 클래스 + 6 | 임베딩 및 DB |
| `input_classifier.py` | ~100 | 3 | 의도 분류 |
| `rag_handler.py` | ~150 | 6 | RAG 및 웹 검색 |
| `map_handler.py` | ~180 | 6 | 지도 처리 |
| `llm_generator.py` | ~250 | 6 | LLM 응답 생성 |
| `evaluation_controller.py` | ~250 | 8 | 응답 평가 |
| `main.py` | ~350 | 4 | 워크플로우 |
| **합계** | ~1,500 | 35+ | - |

---

## 💻 사용 예제

### 1. 색인 구축 (초기 설정)

```python
from main import indexing_workflow

# 의료 문서들을 벡터 DB에 인덱싱
document_paths = [
    "data/disease/disease_001.json",
    "data/disease/disease_002.json",
    "data/disease/disease_003.json"
]

success = indexing_workflow(document_paths)
if success:
    print("✅ 색인 구축 완료!")
```

### 2. 단일 쿼리 처리

```python
from main import main_workflow

# 사용자 쿼리 처리
query = "강아지 피부염 증상이 뭐예요?"
response = main_workflow(query)
print(response)
```

### 3. 배치 처리

```python
from main import batch_workflow

queries = [
    "강아지 피부 질환 증상?",
    "서울 강남역 근처 병원",
    "반려동물 예방 접종"
]

results = batch_workflow(queries)

for result in results:
    print(f"쿼리: {result['query']}")
    print(f"분류: {result['query_type']}")
    print(f"점수: {result['evaluation_score']:.0%}\n")
```

### 4. 특정 모듈만 사용

```python
# 입력 분류만 사용
from input_classifier import classify_query
query_type = classify_query("강아지 피부염?")
print(query_type)  # "medical_consultation"

# 검색만 사용
from rag_handler import search_with_fallback
context, source = search_with_fallback("피부염 증상")
print(f"출처: {source}")  # "rag" 또는 "web"
```

---

## ✨ 스켈레톤 코드의 특징

### ✅ 장점

1. **단순성** - 복잡한 구현 로직 제거, 핵심만 남김
2. **명확한 구조** - 모듈별 책임이 명확함
3. **풍부한 문서화** - Docstring과 상세한 주석
4. **독립성** - 각 모듈을 독립적으로 사용 가능
5. **확장성** - 새로운 모듈 추가 용이
6. **테스트 가능** - 더미 데이터로 즉시 테스트 가능

### 📝 코드 특징

- ✅ 타입 힌팅 (Type Hints) 포함
- ✅ 상세한 Docstring 작성
- ✅ TODO 주석으로 구현 위치 표시
- ✅ 기본 에러 처리 구조
- ✅ 로깅 프린트 포함
- ✅ 각 모듈 테스트 코드 포함

---

## 🚀 구현 로드맵

### Phase 1: 기본 API 연결 (1-2주)
- [ ] OpenAI GPT API 연결
- [ ] Chroma 벡터 DB 로드
- [ ] 임베딩 모델 초기화
- [ ] 카카오맵 API 연결

### Phase 2: 모듈별 구현 (2-3주)
- [ ] data_processor: 파일 로딩 및 청킹 구현
- [ ] vector_store_manager: 벡터 저장소 구현
- [ ] input_classifier: LLM/휴리스틱 분류 구현
- [ ] rag_handler: RAG 검색 구현
- [ ] map_handler: 지도 API 연결
- [ ] llm_generator: 프롬프트 최적화
- [ ] evaluation_controller: 평가 로직 구현

### Phase 3: 통합 및 최적화 (1-2주)
- [ ] main.py 전체 테스트
- [ ] 에러 핸들링 추가
- [ ] 성능 모니터링
- [ ] 캐싱 구현

### Phase 4: 고급 기능 (2주+)
- [ ] 멀티턴 대화
- [ ] 사용자 피드백 학습
- [ ] 분석 대시보드
- [ ] 비용 최적화

---

## 📂 디렉토리 구조

```
skeleton/
│
├── 핵심 모듈 (8개 Python 파일)
│   ├── data_processor.py           (문서 전처리)
│   ├── vector_store_manager.py     (임베딩 및 DB)
│   ├── input_classifier.py         (의도 분류)
│   ├── rag_handler.py              (검색)
│   ├── map_handler.py              (지도)
│   ├── llm_generator.py            (LLM)
│   ├── evaluation_controller.py    (평가)
│   └── main.py                     (오케스트레이션)
│
├── 문서
│   ├── README.md                   (개요 및 가이드)
│   ├── ARCHITECTURE.md             (아키텍처 설계)
│   ├── QUICKSTART.md               (5분 시작 가이드)
│   ├── SUMMARY.md                  (이전 6모듈 요약)
│   └── SKELETON_8_MODULES.md       (이 문서)
│
└── 설정
    ├── requirements.txt            (의존 패키지)
    └── __pycache__/               (컴파일된 바이트코드)

총 13개 파일
```

---

## 🔗 모듈 간 데이터 흐름

### 입력 → 분류 → 검색 → 응답 → 평가 → 출력

```
사용자 쿼리
    │
    ▼
┌────────────────────────┐
│ input_classifier       │
│ classify_query()       │
└────────┬───────────────┘
         │
    분류 결과 (문자열)
         │
    ┌────┴─────┬────────────┐
    │           │            │
    ▼           ▼            ▼
medical      map          general
    │           │            │
    └───────────┼────────────┘
                │
            ▼
    ┌──────────────────────┐
    │ rag/map/web handler  │
    │ search_with_fallback │
    └────────┬─────────────┘
             │
        컨텍스트 (문자열)
             │
             ▼
    ┌──────────────────────┐
    │ llm_generator        │
    │ generate_response()  │
    └────────┬─────────────┘
             │
        초기 응답 (문자열)
             │
             ▼
    ┌──────────────────────────┐
    │ evaluation_controller    │
    │ evaluate_response()      │
    └────────┬─────────────────┘
             │
        평가 결과 (딕셔너리)
             │
       ┌─────┴─────┐
       │            │
    PASS?      REWRITE?
       │            │
       YES      YES (loop)
       │            │
       └─────┬──────┘
            │
            ▼
    ┌──────────────────┐
    │ 최종 답변 + 메트릭│
    └──────────────────┘
```

---

## 🔐 보안 및 안전성

### 의료 정보 처리
- ✅ 면책 조항 자동 포함
- ✅ 응급 경고 표시
- ✅ 정확성 검증 필수

### API 키 관리
- 환경변수에서 로드
- `.env` 파일 사용 (절대 커밋 금지)

### 입력 검증
- 쿼리 길이 제한
- 특수문자 필터링

---

## 📞 다음 단계

1. **이 문서 검토** - 8개 모듈의 목적과 책임 확인
2. **각 모듈 테스트** - 더미 데이터로 작동 확인
3. **Phase 1 구현 시작** - API 연결 및 실제 로직 구현
4. **통합 테스트** - 모듈 간 통합 확인

---

## ✅ 완성 체크리스트

- [x] 8개 핵심 모듈 작성 완료
- [x] 함수/클래스 시그니처 정의
- [x] 상세 Docstring 작성
- [x] 더미 데이터 반환 로직 구현
- [x] TODO 주석으로 구현 위치 표시
- [x] 타입 힌팅 추가
- [x] 기본 에러 처리 구조
- [x] 각 모듈 테스트 코드 포함
- [x] 모듈 간 의존성 명확하게 설계
- [x] 통합 워크플로우 구현
- [x] 색인 워크플로우 추가 (indexing_workflow)
- [x] 배치 처리 워크플로우 (batch_workflow)

---

## 🎓 학습 자료

### 각 모듈 학습 순서 (추천)

1. **input_classifier.py** - 가장 간단한 모듈부터 시작
2. **data_processor.py** - 파일 입출력 이해
3. **vector_store_manager.py** - 벡터 DB 개념
4. **rag_handler.py** - 검색 로직
5. **map_handler.py** - API 통합
6. **llm_generator.py** - LLM 프롬프트
7. **evaluation_controller.py** - 평가 및 제어 로직
8. **main.py** - 통합 워크플로우

---

## 💡 핵심 설계 원칙

### 1. 단일 책임 원칙 (SRP)
각 모듈은 하나의 책임만 가짐

### 2. 느슨한 결합 (Loose Coupling)
모듈 간 의존성 최소화

### 3. 강한 응집력 (High Cohesion)
관련 함수/클래스를 한 모듈에 묶음

### 4. 명확한 인터페이스
각 함수의 입출력이 명확

### 5. 테스트 가능성
각 모듈을 독립적으로 테스트 가능

---

## 📈 성능 예상

| 항목 | 스켈레톤 | 구현 후 |
|------|---------|--------|
| 단일 쿼리 처리 시간 | ~2-3초 | ~3-5초 |
| 색인 구축 시간 (100개 문서) | ~5초 | ~30-60초 |
| 배치 처리 (10개 쿼리) | ~25초 | ~40-60초 |
| 메모리 사용 | ~50MB | ~200-300MB |
| API 호출 비용 | 없음 | 쿼리당 $0.001-0.01 |

---

## 🎯 결론

이 8개 모듈 스켈레톤은:

✅ **복잡한 RAG 시스템을 단순화**  
✅ **명확한 모듈별 책임 정의**  
✅ **쉬운 구현 및 확장**  
✅ **즉시 테스트 가능**  
✅ **프로덕션 준비 가능한 구조**

제공하는 최소한의 기초 프레임워크입니다.

---

**작성자**: AI Assistant  
**완성일**: 2025-12-05  
**버전**: 1.0 (8개 모듈 완성)  
**상태**: ✅ 제출 가능

