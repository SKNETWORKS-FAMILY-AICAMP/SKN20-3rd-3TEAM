# 🐾 반려동물 전문 QA 및 병원 안내 고급 RAG 시스템

## 📋 목차

1. [개요](#개요)
2. [시스템 아키텍처](#시스템-아키텍처)
3. [설치 및 설정](#설치-및-설정)
4. [사용 방법](#사용-방법)
5. [질문 분류 체계](#질문-분류-체계)
6. [각 모듈 상세 설명](#각-모듈-상세-설명)
7. [API 및 기능](#api-및-기능)
8. [결과 예시](#결과-예시)

---

## 개요

이 시스템은 반려동물 관련 질문을 **자동 분류**하여 최적의 처리 방식을 적용하는 고급 RAG(Retrieval-Augmented Generation) 기반 어시스턴트입니다.

### 🎯 핵심 특징

- **🤖 지능형 질문 분류**: 의료/병원/일반 질문 자동 분류
- **📚 다층 검색 시스템**: 내부 데이터 → 근거 평가 → 웹 검색 폴백
- **⭐ 근거 기반 답변**: 각 답변에 신뢰도 및 출처 명시
- **🏥 병원 검색 통합**: 위치 기반 동물병원 정보 제공
- **📊 상세한 메타데이터**: 모든 결과에 신뢰도, 출처, 분류 정보 포함

---

## 시스템 아키텍처

```
사용자 질문
    ↓
[1단계] 질문 분류 (QuestionClassifier)
    ├─→ 의료 질문 (Type A)
    ├─→ 병원 질문 (Type B)
    └─→ 일반 질문 (Type C)
    ↓
[2단계] 유형별 처리
    ├─→ (A) 의료 질문 처리
    │    ├─ 내부 Chroma 검색
    │    ├─ 근거 점수 평가
    │    ├─ Threshold 판단
    │    └─ 웹 검색 폴백 (필요시)
    │
    ├─→ (B) 병원 질문 처리
    │    ├─ CSV 데이터 조회
    │    ├─ 위치 기반 필터링
    │    └─ Kakao Map API (선택)
    │
    └─→ (C) 일반 질문 처리
         └─ LLM 직접 답변
    ↓
[3단계] 답변 생성 및 출처 표시
    ↓
최종 답변 반환
```

---

## 설치 및 설정

### 1. 필수 환경변수 설정

`.env` 파일 생성:

```env
OPENAI_API_KEY=your_openai_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here  # 웹 검색용 (선택)
KAKAO_MAP_API_KEY=your_kakao_map_key_here  # 지도용 (선택)
```

### 2. 필수 라이브러리 설치

```bash
pip install -r requirements.txt
```

### 3. 데이터 구조 확인

```
data/
├── raw/
│   ├── disease/  # JSON 형식 질병 정보 (약 215개)
│   └── hospital/ # CSV 형식 병원 정보
└── Validation/
    └── 01.원천데이터/  # 학습 데이터
```

---

## 사용 방법

### 방법 1: 대화형 모드

```bash
python advanced_main.py
# 메뉴에서 "2. 대화형 모드" 선택
```

### 방법 2: Python 스크립트로 직접 사용

```python
from src.advanced_rag_pipeline import AdvancedRAGPipeline
from src.embeddings import get_embedding_model, load_vectorstore

# 벡터스토어 로드
embedding_model = get_embedding_model("openai")
vectorstore = load_vectorstore(
    embedding_model,
    persist_directory="./chroma_db",
    collection_name="rag_collection"
)

# 파이프라인 초기화
pipeline = AdvancedRAGPipeline(vectorstore)

# 질문 처리
result = pipeline.process_question("개의 피부염 증상은 무엇인가요?")

# 결과 접근
print(result['formatted_answer'])
print(f"분류: {result['classification_type']}")
print(f"신뢰도: {result['classification_confidence']:.2%}")
```

### 방법 3: 배치 처리

```bash
# queries.txt 파일에 질문 작성 (줄 단위)
python advanced_main.py
# 메뉴에서 "3. 배치 처리" 선택
# 결과는 batch_results.json에 저장
```

### 방법 4: 테스트 실행

```bash
python test_advanced_rag.py
```

---

## 질문 분류 체계

### Type A: 의료 관련 질문

**특징**:
- 증상, 질병, 치료, 진단, 예방 등 의료 관련 정보 요청
- 내부 Chroma 벡터스토어 우선 검색
- 근거 점수 기반 신뢰도 평가

**예시**:
- "개의 피부염 증상은 무엇인가요?"
- "고양이가 자꾸 구토해요. 뭐가 문제인가요?"
- "벼룩 예방 방법을 알려주세요."

**처리 흐름**:
```
질문 → 내부 검색 → 근거 평가 (Threshold: 0.6)
  ├─ 점수 ≥ 0.6 → 내부 데이터만 사용
  └─ 점수 < 0.6 → 웹 검색 추가 수행
```

---

### Type B: 병원/지도 질문

**특징**:
- 동물병원 위치, 주소, 연락처 등 정보 요청
- CSV 데이터베이스에서 직접 조회
- 지역별, 병원명별 검색 지원

**예시**:
- "강남구의 동물병원을 찾아주세요."
- "24시간 응급진료 병원이 있을까요?"
- "서울시 동물병원 통계를 보여주세요."

**처리 흐름**:
```
질문 → CSV 데이터 조회
  ├─ 위치 기반 필터링
  ├─ 병원명 검색
  └─ 통계 정보 제공
```

**제공 정보**:
- 병원명
- 주소
- 전화번호
- 허가상태
- 영업형태
- 구별 병원 통계

---

### Type C: 일반 질문

**특징**:
- 의료나 병원 정보가 아닌 일반적인 질문
- OpenAI LLM 직접 활용
- 외부 데이터 검증 없음

**예시**:
- "반려동물을 처음 키우는데 어떤 준비가 필요할까요?"
- "개와 고양이는 왜 사이가 안 좋나요?"

**처리 흐름**:
```
질문 → LLM 직접 답변 → 결과 반환
```

---

## 각 모듈 상세 설명

### 1. QuestionClassifier (src/question_classifier.py)

**역할**: 사용자 질문을 3가지 유형으로 자동 분류

**특징**:
- 2단계 분류: 키워드 기반 → LLM 기반
- 신뢰도 점수 제공
- 분류 사유 명시

**주요 메서드**:
```python
classify(query: str) -> Tuple[QuestionType, float, str]
# 반환: (질문유형, 신뢰도, 분류사유)
```

**내부 키워드**:
```python
의료 키워드: 증상, 질병, 질환, 병, 치료, 진단, 수술, 약물, 예방, 감염 등 (20+)
병원 키워드: 동물병원, 병원, 수의사, 진료, 위치, 지도, 주소, 전화 등 (15+)
```

---

### 2. MedicalQAHandler (src/medical_qa_handler.py)

**역할**: Type A 의료 질문 처리

**주요 기능**:

#### 2-1. 내부 문서 검색
```python
_search_internal_documents(query: str) -> List[Dict]
```
- Chroma 벡터스토어에서 top-k 유사 문서 검색
- 거리 점수를 관련성 점수(0-1)로 변환

#### 2-2. 근거 평가
```python
_evaluate_relevance(documents: List, query: str) -> Tuple[List, float]
```
- LLM을 사용한 세부 관련성 평가
- 각 문서에 0-1 점수 부여
- 평균 근거 점수 계산

**평가 기준**:
1. 질문에 대한 직접적인 답변 제공 여부
2. 정보의 신뢰도 및 정확성
3. 현재성 및 적용 가능성

#### 2-3. 웹 검색 폴백
```python
_web_search(query: str) -> List[Dict]
```
- Tavily Search API 활용
- 근거 점수 threshold 미만시 자동 실행
- 최대 3개 결과 반환

#### 2-4. RAG 기반 답변 생성
```python
_generate_answer_with_rag(query: str, documents: List) -> str
```
- 상위 3개 문서 컨텍스트 활용
- 관련성 점수와 출처 표시

**전체 처리**:
```python
handle_medical_question(query: str) -> Dict
```

반환 정보:
- `answer`: 생성된 답변
- `internal_search_results`: 내부 검색 결과 수
- `web_search_results`: 웹 검색 결과 수
- `relevance_score`: 평균 근거 점수
- `used_web_search`: 웹 검색 사용 여부
- `sources`: 참고 문서 메타데이터

---

### 3. HospitalHandler (src/hospital_handler.py)

**역할**: Type B 병원/지도 질문 처리

**주요 기능**:

#### 3-1. 위치 기반 검색
```python
search_by_location(location: str, radius_km: float) -> List[Dict]
```
- 구명, 동명으로 검색
- 최대 반경 설정 가능

#### 3-2. 병원명 검색
```python
search_by_name(hospital_name: str) -> List[Dict]
```
- 병원명 부분 일치 검색
- 정렬 및 필터링 가능

#### 3-3. 지역별 통계
```python
get_statistics() -> Dict
```
- 구별 병원 수
- 상위 10개 구 통계
- 총 병원 수

#### 3-4. 질문 분석 기반 처리
```python
handle_hospital_question(query: str) -> Dict
```

처리 로직:
1. 특정 병원명 포함 → 병원명 검색
2. 지역명(구/동) 포함 → 위치 검색
3. 일반 정보 요청 → 통계 제공

반환 정보:
- `hospitals`: 검색된 병원 정보 리스트
- `statistics`: 통계 정보
- `response`: 포맷된 응답 문자열

**반환되는 병원 정보**:
```python
{
    'name': '병원명',
    'address': '주소',
    'phone': '전화번호',
    'district': '구명',
    'status': '허가상태',
    'business_type': '영업형태'
}
```

---

### 4. AdvancedRAGPipeline (src/advanced_rag_pipeline.py)

**역할**: 전체 시스템 통합 및 조율

**주요 메서드**:

#### 처리 메인 함수
```python
process_question(query: str) -> Dict
```

반환 구조:
```python
{
    'question': '원본 질문',
    'classification_type': 'A' | 'B' | 'C',
    'classification_confidence': 0.0-1.0,
    'classification_reason': '분류 사유',
    'answer': '답변 내용',
    'formatted_answer': '포맷된 답변',
    'sources': [소스 정보들],
    'timestamp': 'ISO8601 타임스탬프',
    # 유형별 추가 정보
}
```

#### 대화형 모드
```python
interactive_mode()
```
- 무한 반복 질답
- 키보드 인터럽트 처리
- 에러 핸들링

#### 배치 처리
```python
batch_process_questions(questions: List[str]) -> List[Dict]
```

#### 결과 저장
```python
save_results(results: List[Dict], output_path: str = "results.json")
```

---

## API 및 기능

### 주요 클래스 및 메서드

#### QuestionClassifier
| 메서드 | 역할 | 입력 | 출력 |
|--------|------|------|------|
| `classify()` | 질문 분류 | `str` | `(QuestionType, float, str)` |
| `_check_keywords()` | 키워드 매칭 | `str, List` | `float` |
| `_classify_with_llm()` | LLM 분류 | `str` | `QuestionType` |

#### MedicalQAHandler
| 메서드 | 역할 | 입력 | 출력 |
|--------|------|------|------|
| `handle_medical_question()` | 의료 질문 처리 | `str` | `Dict` |
| `_search_internal_documents()` | 내부 검색 | `str` | `List[Dict]` |
| `_evaluate_relevance()` | 근거 평가 | `List, str` | `(List, float)` |
| `_web_search()` | 웹 검색 | `str` | `List[Dict]` |
| `_generate_answer_with_rag()` | RAG 답변 | `str, List` | `str` |

#### HospitalHandler
| 메서드 | 역할 | 입력 | 출력 |
|--------|------|------|------|
| `handle_hospital_question()` | 병원 질문 처리 | `str` | `Dict` |
| `search_by_location()` | 위치 검색 | `str, float` | `List[Dict]` |
| `search_by_name()` | 병원명 검색 | `str` | `List[Dict]` |
| `get_nearby_hospitals()` | 근처 병원 | `str, int` | `List[Dict]` |
| `get_statistics()` | 통계 조회 | 없음 | `Dict` |

#### AdvancedRAGPipeline
| 메서드 | 역할 | 입력 | 출력 |
|--------|------|------|------|
| `process_question()` | 메인 처리 | `str` | `Dict` |
| `interactive_mode()` | 대화형 모드 | 없음 | 없음 |
| `batch_process_questions()` | 배치 처리 | `List[str]` | `List[Dict]` |
| `save_results()` | 결과 저장 | `List, str` | 없음 |

---

## 결과 예시

### Example 1: 의료 질문 (Type A)

**입력**:
```
"개의 피부염 증상은 무엇인가요?"
```

**처리 과정**:
```
[1/3] 질문 분류 중...
  분류 결과: MEDICAL (신뢰도: 0.85)
  사유: 키워드 기반 의료 질문

[2/3] 의료 질문 처리 모듈 실행...
  1단계: 내부 문서 검색 중...
    → 5개 문서 발견
  2단계: 근거 관련성 평가 중...
    → 평균 관련성 점수: 0.78
  3단계: 웹 검색 필요 여부 판단
    → 내부 문서 충분 (Threshold: 0.60)
```

**출력 예시**:
```
📝 답변:
개의 피부염의 주요 증상은 다음과 같습니다:

1. 피부 증상
   - 빨간 반점 (홍반)
   - 가려움증 (소양증)
   - 발진 및 구진
   - 피부 박편화

2. 이차 증상
   - 탈모
   - 피부 감염
   - 냄새 증가

3. 행동 증상
   - 과도한 핥기
   - 긁기

────────────────────────────────────────────────────────
📊 근거 정보:
  • 근거 점수: 78%
  • 내부 문서: 5개
  • 웹 검색 활용: 아니오

📚 주요 출처:
  1. disease_data_001.json (85% 관련성)
     부서: 피부과
  2. disease_data_015.json (78% 관련성)
     부서: 피부과
  3. disease_data_042.json (72% 관련성)
     부서: 내과
```

---

### Example 2: 병원 질문 (Type B)

**입력**:
```
"강남구의 동물병원을 찾아주세요."
```

**처리 과정**:
```
[1/3] 질문 분류 중...
  분류 결과: HOSPITAL (신뢰도: 0.92)
  사유: 키워드 기반 병원 질문

[2/3] 병원/지도 질문 처리 모듈 실행...
  지역 검색: 강남구
  → 87개 병원 발견
```

**출력 예시**:
```
🔍 검색 결과: 87개 병원 발견

🏥 강남동물병원
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📍 주소: 서울특별시 강남구 강남대로 123
📞 전화: 02-1234-5678
상태: 정상
영업형태: 개인동물의료

🏥 서울24시간동물의료센터
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📍 주소: 서울특별시 강남구 테헤란로 456
📞 전화: 02-9876-5432
상태: 정상
영업형태: 동물의료법인

[... 더 많은 결과 ...]

📊 병원 통계:
총 병원 수: 5,287

구별 병원 수 (상위 10개):
  • 강남구: 387개
  • 서초구: 342개
  • 송파구: 315개
  • 강동구: 298개
  • [... 더 ...]
```

---

### Example 3: 일반 질문 (Type C)

**입력**:
```
"반려동물을 처음 키우는데 어떤 준비가 필요할까요?"
```

**처리 과정**:
```
[1/3] 질문 분류 중...
  분류 결과: GENERAL (신뢰도: 0.88)
  사유: LLM 기반 일반 질문 분류

[2/3] 일반 질문 처리 모듈 실행...
```

**출력 예시**:
```
📝 답변:
반려동물을 처음 키우실 때 필요한 준비 사항을 정리하면 다음과 같습니다:

1. 집 준비
   - 반려동물의 안전한 공간 확보
   - 필요한 용품: 식기, 침구, 장난감
   - 안전한 환경 조성 (위험물 제거)

2. 필수 용품
   - 고품질 사료 및 물
   - 화장실/배변 용품
   - 목줄, 하네스, 캐리어

3. 의료 준비
   - 수의사 선정
   - 초기 건강 검진
   - 예방접종 일정 파악
   - 보험 가입 검토

4. 교육 및 훈련
   - 기본 명령어 교육
   - 사회화 훈련
   - 배변 훈련

5. 시간 관리
   - 충분한 산책 시간
   - 놀이 및 상호작용 시간
   - 정기적인 그루밍
```

---

## 구성 파일 목록

```
src/
├── question_classifier.py      # 질문 분류 모듈
├── medical_qa_handler.py       # 의료 질문 처리
├── hospital_handler.py         # 병원 정보 처리
├── advanced_rag_pipeline.py    # 통합 파이프라인
├── ingestion.py                # 데이터 로드 (기존)
├── chunking.py                 # 문서 분할 (기존)
├── embeddings.py               # 임베딩 처리 (기존)
├── retrieval.py                # 검색 (기존)
└── pipeline.py                 # 기본 파이프라인 (기존)

advanced_main.py               # 고급 시스템 메인 실행
test_advanced_rag.py          # 테스트 스크립트
ADVANCED_RAG_README.md        # 본 문서
```

---

## 주의사항

1. **API 키**: OpenAI API 키는 필수이며, Tavily API 키는 선택사항
2. **데이터 경로**: 병원 CSV 파일 경로가 정확한지 확인
3. **벡터스토어**: 첫 실행시 시간이 소요될 수 있음
4. **Rate Limiting**: API 호출 제한에 주의

---

## 문제 해결

### Q: "벡터스토어를 찾을 수 없습니다" 오류
**A**: 다음 명령 실행:
```bash
python advanced_main.py  # 메뉴에서 "1. 예시 질문 실행" 선택
```

### Q: API 키 오류
**A**: `.env` 파일이 올바르게 설정되었는지 확인:
```bash
cat .env  # Linux/Mac
type .env  # Windows
```

### Q: 병원 데이터가 표시되지 않음
**A**: CSV 파일 경로 확인:
```bash
ls data/raw/hospital/  # 또는 dir data\raw\hospital\ (Windows)
```

---

## 향후 개선 계획

- [ ] Kakao Map API 통합 (지도 시각화)
- [ ] 다국어 지원 (영어, 일본어 등)
- [ ] 임베딩 모델 다양화 (local models)
- [ ] 대화 히스토리 관리
- [ ] 개인화된 질답 학습
- [ ] 정기적인 근거 데이터 업데이트
- [ ] 챗봇 UI (Streamlit/Gradio)

---

## 라이센스

이 프로젝트는 반려동물 의료 정보 제공 목적으로 사용됩니다.

---

## 문의 및 지원

더 자세한 정보는 개발자에게 문의하세요.

---

**마지막 업데이트**: 2025년 12월 3일
**버전**: 2.0 (Advanced RAG)

