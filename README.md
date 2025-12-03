# 반려동물 증상 분석 및 맞춤 병원 추천 챗봇

RAG(검색 증강 생성) 기술을 활용한 반려동물 건강 상담 시스템입니다. 증상 입력 시 수의학 전문 지식 기반으로 의심 질환을 분석하고, 필요시 맞춤형 동물병원을 추천합니다.

## 🎯 주요 기능

1. **증상 분석 (RAG 기반)**
   - 수의학 전문 말뭉치 데이터를 활용한 신뢰도 높은 답변
   - 진료과별(내과/외과/안과/치과/피부과) 메타데이터 필터링

2. **응급도 판단**
   - AI 기반 자동 트리아지 (높음/보통/낮음)
   - 응급 상황 시 즉시 병원 방문 권장

3. **맞춤 병원 추천**
   - 지역 및 진료과 기반 동물병원 추천
   - 24시간 운영 병원 우선 안내 (응급도 높음 시)

4. **LangGraph 워크플로우**
   - 증상 분석 → 응급도 판단 → 병원 추천 자동화
   - 조건부 분기를 통한 최적화된 응답

## 🛠️ 기술 스택

- **LLM**: Claude Sonnet 4.5 / Opus 4.5 (Anthropic)
- **프레임워크**: LangChain, LangGraph
- **Vector DB**: ChromaDB
- **임베딩**: jhgan/ko-sbert-nli (한국어 특화)
- **언어**: Python 3.10+

## 📁 프로젝트 구조

```
3rd_prj/
│
├── src/
│   ├── data/
│   │   └── preprocessing.py      # 데이터 로드 및 전처리
│   ├── rag/
│   │   └── pipeline.py           # RAG 파이프라인 구축
│   ├── agent/
│   │   └── workflow.py           # LangGraph Agent 워크플로우
│   └── utils/
│       └── tools.py              # Agent Tools (RAG 검색, 병원 추천)
│
├── config/
│   └── .env.example              # 환경 변수 템플릿
│
├── data/
│   └── 59.반려견 성장 및 질병 관련 말뭉치 데이터/
│
├── main.py                       # 통합 실행 스크립트
├── requirements.txt              # 의존성 패키지
└── README.md                     # 이 파일
```

## 🚀 설치 및 실행

### 1. 의존성 설치

```bash
pip install -r requirements.txt
```

### 2. 환경 변수 설정

`config/.env.example`을 복사하여 `config/.env` 파일을 생성하고 API 키를 입력하세요.

```bash
cp config/.env.example config/.env
```

`.env` 파일 내용:
```
ANTHROPIC_API_KEY=your_actual_api_key_here
```

### 3. 데이터 준비

데이터 경로를 실제 환경에 맞게 수정하세요.

- `main.py`의 `base_path` 변수

### 4. 실행

#### 전체 파이프라인 실행
```bash
python main.py
```

#### 개별 모듈 테스트

**데이터 전처리만 테스트:**
```bash
python src/data/preprocessing.py
```

**RAG 파이프라인만 테스트:**
```bash
python src/rag/pipeline.py
```

**LangGraph Agent만 테스트:**
```bash
python src/agent/workflow.py
```

## 📊 데이터 구조

### A. 원천 데이터 (TS_말뭉치데이터)

```json
{
  "title": "소동물 주요 질환의 임상추론...",
  "author": "현창백 내과아카데미 역",
  "publisher": "(주)범문에듀케이션",
  "department": "내과",
  "disease": "황달 증례의 임상적 추론... (긴 전문 텍스트)"
}
```

- **활용**: `disease` 필드를 RAG 지식 베이스로 사용
- **메타데이터**: `department`를 검색 필터로 활용

### B. 라벨링 데이터 (TL_질의응답데이터)

```json
{
  "meta": {
    "lifeCycle": "자견",
    "department": "내과",
    "disease": "기타"
  },
  "qa": {
    "instruction": "너는 반려견 건강 전문가야...",
    "input": "저희 집 강아지가 구토를 하고...",
    "output": "질문 내용을 확인하였습니다..."
  }
}
```

- **활용**: `qa.instruction`을 System Prompt 정의에 참고
- **메타데이터**: Query Re-writing 및 검색 조건 부여

## 🔄 워크플로우 상세

### LangGraph Agent 워크플로우

```
[시작]
  ↓
[Node 1: analyze_symptom]
  - RAG 검색 수행
  - 증상 분석 결과 저장
  ↓
[Node 2: triage_and_decide]
  - LLM 기반 응급도 판단
  - 추천 진료과 결정
  ↓
[조건부 분기]
  ├─ 응급도 "높음/보통" → [Node 3: recommend_hospital]
  │                         - 병원 검색 및 추천
  │                         ↓
  └─ 응급도 "낮음" ────────→ [Node 4: generate_final_response]
                             - 최종 응답 생성
                             ↓
                           [종료]
```

## 🧪 테스트 예제

```python
from src.agent.workflow import run_agent

# 응급도 높음 케이스
result = run_agent(
    "저희 강아지가 갑자기 구토를 여러 번 하고 배가 부풀어 올랐어요.",
    config={"configurable": {"thread_id": "test_1"}}
)
print(result["final_response"])

# 응급도 낮음 케이스
result = run_agent(
    "고양이 눈이 약간 충혈되었는데 평소와 다를 게 없어요.",
    config={"configurable": {"thread_id": "test_2"}}
)
print(result["final_response"])
```

## 📈 향후 개선 사항

### 단기 (1-2주)
- [ ] 실제 카카오맵 API 연동
- [ ] 사용자 위치 정보 입력 기능
- [ ] 웹 인터페이스 개발 (Streamlit/Gradio)

### 중기 (1개월)
- [ ] 대화 히스토리 관리 (멀티턴 대화)
- [ ] 질문 정제(Query Re-writing) 기능 추가
- [ ] 라벨링 데이터를 활용한 Few-shot Learning

### 장기 (3개월+)
- [ ] 사용자 피드백 수집 및 평가 시스템
- [ ] Fine-tuning을 통한 도메인 특화 모델 개발
- [ ] 다국어 지원 (영어, 일본어 등)
- [ ] 모바일 앱 개발

## 🔑 핵심 함수 설명

### 1. `load_and_preprocess_data()` - `src/data/preprocessing.py`
- **기능**: JSON 데이터 로드, 텍스트 정제, 청킹, Document 객체 생성
- **파라미터**:
  - `file_path`: 데이터 파일 또는 디렉토리 경로
  - `chunk_size`: 청크 크기 (기본 1000)
  - `chunk_overlap`: 오버랩 크기 (기본 200)
  - `data_type`: "source" 또는 "labeled"

### 2. `setup_rag_pipeline()` - `src/rag/pipeline.py`
- **기능**: Vector Store, Retriever, LLM Chain 구성
- **파라미터**:
  - `documents`: Document 리스트
  - `embedding_model`: 임베딩 모델명
  - `model_name`: Claude 모델명
  - `k`: 검색할 문서 수 (기본 4)
  - `filter_metadata`: 메타데이터 필터 (옵션)

### 3. `create_pet_health_agent()` - `src/agent/workflow.py`
- **기능**: LangGraph 워크플로우 정의 및 컴파일
- **반환**: 실행 가능한 StateGraph 앱

### 4. `run_agent()` - `src/agent/workflow.py`
- **기능**: Agent 실행 및 결과 반환
- **파라미터**:
  - `user_query`: 사용자 질문
  - `config`: LangGraph 설정 (thread_id 등)

## 📄 라이센스

이 프로젝트는 MIT 라이센스 하에 배포됩니다.

## 📧 문의

프로젝트 관련 문의사항은 이슈를 등록해주세요.

---

**Made with ❤️ for Pet Health**
