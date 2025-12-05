# 🚀 RAG 어시스턴트 스켈레톤 - 시작하기

**목표**: 5분 내에 8개 모듈 스켈레톤 코드 이해 및 테스트

---

## ⚡ 30초 요약

이 프로젝트는 **복잡한 RAG 시스템을 8개의 최소 기초 모듈로 단순화**한 것입니다.

| 모듈 | 역할 |
|------|------|
| 1️⃣ `data_processor.py` | 문서 전처리 및 청킹 |
| 2️⃣ `vector_store_manager.py` | 임베딩 및 벡터 DB |
| 3️⃣ `input_classifier.py` | 사용자 의도 분류 |
| 4️⃣ `rag_handler.py` | RAG 및 웹 검색 |
| 5️⃣ `map_handler.py` | 지도 정보 조회 |
| 6️⃣ `llm_generator.py` | LLM 응답 생성 |
| 7️⃣ `evaluation_controller.py` | 응답 평가 및 제어 |
| 8️⃣ `main.py` | 전체 워크플로우 |

---

## 📋 파일 구조

```
skeleton/
├── 핵심 모듈 (8개 Python 파일) ⭐ 핵심
├── 문서 (5개 마크다운)
│   ├── 00_START_HERE.md           ← 이 문서
│   ├── SKELETON_8_MODULES.md      ← 상세 설명 (읽어야 할 문서!)
│   ├── QUICKSTART.md              ← 5분 시작 가이드
│   ├── ARCHITECTURE.md            ← 아키텍처 설계
│   └── README.md                  ← 전체 개요
└── 설정 파일
    └── requirements.txt           ← 의존 패키지
```

**지금 읽어야 할 문서**: `SKELETON_8_MODULES.md` 📖

---

## 🎯 3가지 사용 시나리오

### 시나리오 1: 코드 이해하기 (5분)

```bash
# 1. 각 모듈의 용도 확인
$ head -20 data_processor.py      # 문서 처리
$ head -20 vector_store_manager.py # 벡터 DB
$ head -20 input_classifier.py     # 의도 분류
# ... 나머지 모듈들

# 2. 각 함수의 역할 확인
# 각 파일의 Docstring을 읽으세요 (매우 상세함)

# 3. 워크플로우 확인
$ cat main.py | grep "def main_workflow"
```

### 시나리오 2: 더미 테스트 실행 (3분)

```bash
# Python 실행 (스켈레톤이므로 API 키 불필요)
$ python main.py

# 또는 개별 모듈 테스트
$ python input_classifier.py
$ python data_processor.py
$ python rag_handler.py
```

### 시나리오 3: 구현 시작 (1-2주)

```bash
# 1. Phase 1: 기본 API 연결
# - OpenAI API 키 설정
# - Chroma 벡터 DB 연결
# - 각 모듈의 TODO 주석 확인

# 2. Phase 2: 모듈별 구현
# - data_processor: 파일 로딩
# - vector_store_manager: 벡터 저장
# - input_classifier: 실제 분류
# - rag_handler: 벡터 검색
# - map_handler: API 호출
# - llm_generator: LLM 호출
# - evaluation_controller: 평가 로직

# 3. Phase 3: 통합 테스트
# - main.py 워크플로우 테스트
```

---

## 💻 즉시 테스트하기

### 1단계: 준비

```bash
# 디렉토리로 이동
cd skeleton/

# Python 3.9+ 확인
python --version
```

### 2단계: 기본 테스트 (API 키 불필요!)

```python
# 파이썬 터미널에서

# 테스트 1: 입력 분류
from input_classifier import classify_query
result = classify_query("강아지 피부염 증상?")
print(result)  # "medical_consultation" 출력

# 테스트 2: 벡터 매니저
from vector_store_manager import VectorStoreManager
manager = VectorStoreManager()
stats = manager.get_stats()
print(stats)

# 테스트 3: 전체 워크플로우 (더미 데이터 사용)
from main import main_workflow
response = main_workflow("강아지 피부염?")
print(response)
```

### 3단계: 전체 워크플로우 테스트

```bash
python main.py
```

**예상 출력**:
```
============================================================
🏥 RAG 기반 AI 어시스턴트 - 8개 모듈 스켈레톤 코드
============================================================

### 테스트 1: 색인 구축 워크플로우 ###
...

### 테스트 2: 단일 쿼리 처리 ###
...

### 테스트 3: 배치 처리 ###
...

✅ 테스트 완료!
```

---

## 📖 각 모듈 이해하기 (10분)

### 1️⃣ data_processor.py - 문서 처리

**핵심 함수**: `preprocess_document(file_path) → List[str]`

```python
from data_processor import preprocess_document

# 문서 파일을 읽고 청크로 분할
chunks = preprocess_document("data/disease/disease_001.json")
# 출력: ["청크1 텍스트...", "청크2 텍스트...", ...]
```

**처리 순서**:
```
파일 로드 → 텍스트 추출 → 정제 → 청킹 → 청크 리스트 반환
```

---

### 2️⃣ vector_store_manager.py - 벡터 DB 관리

**핵심 함수**: `embed_and_index_chunks(chunks) → bool`

```python
from vector_store_manager import embed_and_index_chunks

# 청크들을 임베딩하여 DB에 저장
success = embed_and_index_chunks(["청크1", "청크2", "청크3"])
# 출력: True (성공)
```

**처리 순서**:
```
텍스트 청크 → 임베딩 생성 → ID 할당 → DB 저장 → 성공 여부 반환
```

---

### 3️⃣ input_classifier.py - 의도 분류

**핵심 함수**: `classify_query(query) → str`

```python
from input_classifier import classify_query

# 쿼리 의도 분류
result = classify_query("강아지 피부염?")
# 출력: "medical_consultation"

result = classify_query("병원 찾아줘")
# 출력: "map_search"
```

**3가지 분류**:
- `"medical_consultation"`: 의료 관련
- `"map_search"`: 지도/위치 관련
- `"general"`: 일반 질문

---

### 4️⃣ rag_handler.py - 검색

**핵심 함수**: `search_with_fallback(query) → (str, str)`

```python
from rag_handler import search_with_fallback

# RAG 검색, 실패 시 웹 검색으로 자동 폴백
context, source = search_with_fallback("강아지 피부염?")
# 출력: ("검색 결과...", "rag" 또는 "web")
```

**CRAG 패턴** (자동 폴백):
```
쿼리 → RAG 검색 → 관련 문서 있나?
                  ├─ YES: RAG 결과 반환
                  └─ NO: 웹 검색 → 웹 결과 반환
```

---

### 5️⃣ map_handler.py - 지도 처리

**핵심 함수**: `get_map_info(query) → str`

```python
from map_handler import get_map_info

# 병원 정보 조회
info = get_map_info("강남역 근처 병원")
# 출력: "📍 [1번] OO병원\n주소: ...\n거리: ...\n"
```

**처리**:
```
쿼리 → 위치 추출 → API 호출 → 거리 계산 → 정렬 → 포맷팅
```

---

### 6️⃣ llm_generator.py - LLM 응답 생성

**핵심 함수**: `generate_response(query, context) → str`

```python
from llm_generator import generate_response

# LLM을 사용하여 응답 생성
response = generate_response(
    query="강아지 피부염?",
    context="[검색 결과] 피부염 관련..."
)
# 출력: "강아지 피부염은... [면책 조항]"
```

**추가 기능**:
- `build_system_prompt()`: 타입별 프롬프트 생성
- `rewrite_response()`: 피드백 기반 재작성
- `estimate_token_count()`: 토큰 수 추정

---

### 7️⃣ evaluation_controller.py - 응답 평가

**핵심 함수**: `evaluate_response(response) → Dict`

```python
from evaluation_controller import evaluate_response

# 응답 평가 (4개 차원)
evaluation = evaluate_response("강아지 피부염은...")
# 출력:
# {
#     'pass': True,
#     'scores': {
#         'accuracy': 0.85,
#         'clarity': 0.90,
#         'completeness': 0.80,
#         'safety': 0.88
#     },
#     'average_score': 0.858
# }
```

**평가 판정**:
- ✅ `pass=True` (점수 ≥ 0.75): 응답 승인
- 🔄 `pass=False` (점수 < 0.75): 재작성 필요

---

### 8️⃣ main.py - 전체 워크플로우

**3가지 워크플로우**:

#### A. 색인 구축 (초기 설정)

```python
from main import indexing_workflow

# 문서들을 벡터 DB에 인덱싱
success = indexing_workflow([
    "data/disease/disease_001.json",
    "data/disease/disease_002.json"
])
```

#### B. 단일 쿼리 처리 (메인)

```python
from main import main_workflow

# 사용자 쿼리 처리
response = main_workflow("강아지 피부염?")
```

**8단계 워크플로우**:
```
1. 입력 분류
2. 정보 검색 (RAG/지도/웹)
3. 시스템 프롬프트 구성
4. LLM 응답 생성
5. 평가 (4개 차원)
6. 재작성 루프 (필요시)
7. 메트릭 수집
8. 최종 답변 반환
```

#### C. 배치 처리

```python
from main import batch_workflow

# 여러 쿼리 처리
results = batch_workflow([
    "쿼리1",
    "쿼리2",
    "쿼리3"
])
```

---

## 🔄 전체 처리 흐름 (1분)

```
사용자 쿼리
    ↓
[1] 의도 분류 (input_classifier)
    ↓
    ├─ 의료 → RAG 검색
    ├─ 지도 → 지도 API
    └─ 일반 → 웹 검색
    ↓
[2] 정보 검색 (rag_handler / map_handler)
    ↓
[3] 프롬프트 구성 (llm_generator)
    ↓
[4] LLM 응답 생성 (llm_generator)
    ↓
[5] 응답 평가 (evaluation_controller)
    ├─ 정확도, 명확성, 완전성, 안전성 평가
    └─ 점수 계산
    ↓
[6] 재작성 필요? (evaluation_controller)
    ├─ YES (점수 0.50-0.75) → [4]로 돌아가기 (최대 2회)
    ├─ NO (점수 ≥ 0.75) → 승인
    └─ ESCALATE (점수 < 0.50) → 경고 반환
    ↓
[7] 메트릭 수집 (evaluation_controller)
    ↓
✨ 최종 답변 반환
```

---

## ✅ 체크리스트

읽어야 할 것들:

- [ ] 이 문서 (지금 읽는 중)
- [ ] `SKELETON_8_MODULES.md` - 8개 모듈 상세 설명 ⭐⭐⭐ 필독!
- [ ] `ARCHITECTURE.md` - 아키텍처 다이어그램
- [ ] 각 모듈의 Docstring - 코드 주석

테스트해야 할 것들:

- [ ] `python input_classifier.py`
- [ ] `python data_processor.py`
- [ ] `python rag_handler.py`
- [ ] `python main.py` (전체 테스트)

구현 준비:

- [ ] `requirements.txt` 패키지 설치
- [ ] OpenAI API 키 준비
- [ ] 각 모듈의 TODO 주석 확인
- [ ] Phase 1부터 구현 시작

---

## 🎓 학습 경로 (추천)

### 1시간 - 전체 구조 이해

1. **이 문서 읽기** (5분)
2. **SKELETON_8_MODULES.md 읽기** (30분)
3. **각 모듈 코드 훑어보기** (20분)
4. **main.py의 main_workflow 이해** (5분)

### 2시간 - 코드 상세 분석

1. **input_classifier.py 분석** (20분)
2. **data_processor.py 분석** (20분)
3. **vector_store_manager.py 분석** (20분)
4. **나머지 5개 모듈 분석** (40분)

### 1시간 - 테스트 및 실습

1. **더미 데이터로 각 모듈 테스트** (30분)
2. **main_workflow 테스트** (20분)
3. **코드 수정 및 실험** (10분)

---

## 💡 중요 팁

### 1. TODO 주석 따르기

각 함수에 `# TODO:` 주석이 있습니다:

```python
def my_function():
    # TODO: 실제 API 호출 구현
    # - Step 1: ...
    # - Step 2: ...
    
    # 더미 구현
    return dummy_value
```

구현 시 이 주석들을 따라가면 됩니다!

### 2. 타입 힌팅 이해

모든 함수에 타입이 명시되어 있습니다:

```python
def classify_query(query: str) -> str:
    # 입력: 문자열
    # 출력: 문자열
```

이것이 함수를 이해하는 첫 번째 방법입니다.

### 3. Docstring 읽기

각 함수의 Docstring은 매우 상세합니다:

```python
def my_function(arg: Type) -> ReturnType:
    """
    이 함수는...
    
    Args:
        arg: ...
    
    Returns:
        ...: ...
    
    처리 순서:
        1. ...
        2. ...
    
    예시:
        ...
    
    TODO:
        - 구현할 것 1
        - 구현할 것 2
    """
```

Docstring을 자세히 읽으세요!

---

## 🚀 다음 단계

### 지금 할 것 (5분)

1. **SKELETON_8_MODULES.md 읽기** (매우 중요!)
2. **main.py 테스트 실행** (`python main.py`)

### 이번 주 할 것

1. 각 모듈 코드 상세 분석
2. Phase 1 API 연결 준비
3. OpenAI, Chroma 설정

### 이번 달 할 것

1. Phase 1-2 구현
2. 전체 통합 테스트
3. 성능 최적화

---

## ❓ FAQ

**Q: 이 코드를 지금 바로 사용할 수 있나요?**  
A: 아니요. 이것은 스켈레톤입니다. 각 모듈의 TODO 주석을 따라 구현해야 합니다.

**Q: 스켈레톤을 실행할 때 API 키가 필요한가요?**  
A: 아니요! 더미 데이터를 반환하므로 API 없이 테스트할 수 있습니다.

**Q: 어디부터 구현을 시작해야 하나요?**  
A: `input_classifier.py`부터 시작하세요. 가장 간단합니다.

**Q: 기존 코드는 어디에 있나요?**  
A: `../src/` 디렉토리에 있습니다. 참고용으로 사용하세요.

**Q: 도움이 필요하면?**  
A: 각 파일의 Docstring과 TODO 주석을 읽으세요. 매우 상세합니다.

---

## 📞 요약

| 항목 | 설명 |
|------|------|
| **목표** | 복잡한 RAG 시스템을 8개 모듈로 단순화 |
| **코드 형식** | 함수/클래스 시그니처 + 주석만 |
| **구현** | 각 모듈의 TODO 주석 따라가기 |
| **테스트** | 더미 데이터로 즉시 테스트 가능 |
| **문서** | 상세한 Docstring 포함 |
| **예상 시간** | Phase 1-2: 2-3주 |

---

**지금 바로 시작하세요!** 🚀

다음 문서: `SKELETON_8_MODULES.md` 📖
