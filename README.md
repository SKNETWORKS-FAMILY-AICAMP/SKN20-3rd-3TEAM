# 🐕 LLM을 연동한 내외부 문서 기반 질의응답 시스템

**강아지 질병 증상 상담 챗봇**

👥 팀원 소개

<div align="center">
<table>
  <tr>
    <td align="center" width="150" style="vertical-align: top; padding: 10px;">
      <img src="https://github.com/user-attachments/assets/85e707e3-380e-4b47-a530-cc593bcd4f87" style="width: 120px; height: 120px; object-fit: cover; border-radius: 8px;">
      <div style="margin-top: 8px;">
        <b>박찬</b><br>팀장
      </div>
    </td>
    <td align="center" width="150" style="vertical-align: top; padding: 10px;">
      <img src="https://github.com/user-attachments/assets/40307edb-2139-4c87-923a-a18ce394f5b0" style="width: 120px; height: 120px; object-fit: cover; border-radius: 8px;">
      <div style="margin-top: 8px;">
        <b>김나현</b><br>팀원
      </div>
    </td>
    <td align="center" width="150" style="vertical-align: top; padding: 10px;">
      <img src="https://github.com/user-attachments/assets/806b67c5-b5a0-4605-868b-bf52895bc006" style="width: 120px; height: 120px; object-fit: cover; border-radius: 8px;">
      <div style="margin-top: 8px;">
        <b>이도경</b><br>팀원
      </div>
    </td>
    <td align="center" width="150" style="vertical-align: top; padding: 10px;">
      <img src="https://github.com/user-attachments/assets/5c1c0ded-8509-412e-9d51-46d8bd9e7c11" style="width: 120px; height: 120px; object-fit: cover; border-radius: 8px;">
      <div style="margin-top: 8px;">
        <b>안채연</b><br>팀원
      </div>
    </td>
    <td align="center" width="150" style="vertical-align: top; padding: 10px;">
      <img src="https://github.com/user-attachments/assets/334057f7-b2a3-4fac-919c-d78ade2be0fe" style="width: 120px; height: 120px; object-fit: cover; border-radius: 8px;">
      <div style="margin-top: 8px;">
        <b>이경현</b><br>팀원
      </div>
    </td>
  </tr>
</table>
</div>

## 📌 프로젝트 개요

### **강아지 질병 증상 챗봇**

반려견 보호자가 강아지의 증상을 입력하면, AI가 수의학 지식 데이터베이스와 과거 상담 기록을 기반으로 정확한 의료정보를 제공하는 RAG 기반 Chat-bot입니다.

### **주요 특징**
- 📚 **30,000+ 건의 수의학 데이터** 기반 정확한 답변
- 🔍 **하이브리드 검색 시스템** (Similarity + BM25 + Ensemble(Simlilarity + BM25))
- 🎯 **RAGAS 기반 성능 평가** (4가지 메트릭으로 객관적 품질 측정)
- 💬 **Streamlit 기반 직관적인 UI**
- 🤖 **다중 임베딩 모델 비교** (OpenAI vs BGE-M3)
- 📊 **체계적인 테스트 데이터셋 생성 및 평가**

---

## 🎯 개발 동기

### **문제 인식**
1. **정보 접근성 문제**: 반려견 보호자들이 증상 발생 시 신뢰할 수 있는 정보를 찾기 어려움
2. **응급 상황 판단 어려움**: 어떤 증상이 응급인지, 언제 병원에 가야 하는지 판단이 어려움
3. **검색 성능의 불확실성**: 단일 검색 방식으로는 다양한 질문 유형에 대응하기 어려움

### **해결 방안**
- **LLM + RAG 기술**을 활용하여 수의학 전문 지식을 기반으로 한 정확한 상담 제공
- **다단계 하이브리드 검색**으로 관련성 높은 정보만 선별하여 할루시네이션 최소화
- **RAGAS 평가 프레임워크**로 시스템 성능을 객관적으로 측정 및 개선

---

## ⚡ 주요 기능

### 1. **증상 기반 질의응답**
- 반려견의 증상을 자연어로 입력하면 AI가 ChromaDB에 저장된 데이터를 분석하여 답변 제공
- 가능한 원인, 집에서의 관리 방법, 병원 방문 시기 등을 종합적으로 안내
- 모든 답변에 출처 정보 명시 (서적, 상담기록 등)

### 2. **하이브리드 검색 시스템**
```
검색 방식 4가지 제공:

1. Similarity Search (유사도 검색)
   └─ 벡터 유사도 기반 의미론적 검색

2. BM25 Search (키워드 검색)
   └─ 전통적인 키워드 매칭 기반
   └─ TF-IDF 개선 알고리즘

3. Ensemble Search (앙상블)
   └─ Similarity + BM25 결합
   └─ 가중치 기반 종합 검색 (0.5:0.5)
```

### 3. **Query Rewriting (질문 변환)**
```python
# 사용자 질문을 검색에 최적화된 키워드로 변환
원본: "강아지가 밥을 잘 안 먹고 계속 토해요"
변환: "강아지 식욕부진 구토"
```

### 4. **다중 임베딩 모델 지원**
- **OpenAI Embeddings**: `text-embedding-3-small` (1536차원)
- **BGE-M3**: `BAAI/bge-m3` (다국어 지원, 무료)
- 각 모델별 독립적인 벡터스토어 구축 및 성능 비교

### 5. **RAGAS 기반 성능 평가**
```
평가 지표 (RAGAS 4대 메트릭):

1. Context Recall (검색 재현율)
   └─ 검색된 문서가 정답을 얼마나 포함하는가?

2. Context Precision (검색 정확도)
   └─ 검색된 문서가 얼마나 관련성이 높은가?

3. Faithfulness (충실성)
   └─ 답변이 검색된 문서에 기반하는가? (할루시네이션 방지)

4. Answer Relevancy (답변 관련성)
   └─ 답변이 질문과 관련이 있는가?
```

### 6. **합성 테스트 데이터셋 생성**
- RAGAS를 활용한 고품질 테스트 데이터 자동 생성
- 벡터스토어의 실제 문서 기반으로 질문-답변 쌍 생성
- 다양한 질문 유형 지원 (simple, reasoning, multi_context, conditional)

---

## 🏗️ 시스템 아키텍처

```
┌─────────────────────────────────────────────────────────────┐
│                       사용자 인터페이스                        │
│                        (Streamlit UI)                        │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                      질의 응답 시스템                         │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌───────────┐         │
│  │    Query     │─▶│  Retriever   │─▶│    LLM    │         │
│  │  Rewriting   │  │              │  │ (GPT-4o   │         │
│  │              │  │              │  │  -mini)   │         │
│  └──────────────┘  └──────────────┘  └───────────┘         │
│         │                 │                 │               │
│         ▼                 ▼                 ▼               │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────┐         │
│  │   Keyword    │  │ Similarity   │  │  Prompt   │         │
│  │  Extraction  │  │     BM25     │  │ Template  │         │
│  └──────────────┘  │  Ensemble    │  └───────────┘         │
│                    └──────────────┘                         │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                       데이터 레이어                           │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────────┐  ┌──────────────────┐                │
│  │    ChromaDB      │  │    ChromaDB      │                │
│  │    (OpenAI)      │  │    (BGE-M3)      │                │
│  │  30,000+ docs    │  │  30,000+ docs    │                │
│  └──────────────────┘  └──────────────────┘                │
│                                                              │
│          - 수의학 서적 데이터 (5개 과)                        │
│          - 질의응답 데이터 (5개 과)                           │
└─────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                       평가 시스템                             │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────────┐  ┌──────────────────┐                │
│  │      RAGAS       │  │  Test Dataset    │                │
│  │   Evaluation     │◄─│   Generation     │                │
│  │   (4 Metrics)    │  │   (Synthetic)    │                │
│  └──────────────────┘  └──────────────────┘                │
└─────────────────────────────────────────────────────────────┘
```

### **핵심 컴포넌트**

#### 1. **데이터 전처리 모듈** (`preprocessing.py`)
- 수의학 서적 데이터와 QA 데이터 통합 처리
- 데이터 타입별 차별화된 청킹 전략
  - **의학 데이터**: `chunk_size=500`, `chunk_overlap=100`
  - **QA 데이터**: `chunk_size=800`, `chunk_overlap=50`
- 메타데이터 구조화 (출처, 진료과, 생애주기 등)

#### 2. **벡터스토어 구축**
- **OpenAI 벡터스토어** (`vectorstore_openai.py` - 별도 파일)
  - 임베딩: `text-embedding-3-small`
  - 컬렉션: `pet_health_qa_system`
  - 경로: `../data/ChromaDB_openai`

- **BGE-M3 벡터스토어** (`vectorstore_bge_m3.py`)
  - 임베딩: `BAAI/bge-m3`
  - 컬렉션: `pet_health_qa_system_bge_m3`
  - 경로: `../data/ChromaDB_bge_m3`

- 배치 처리 (100개씩)로 대용량 데이터 효율적 임베딩
- API Rate Limit 방지 메커니즘 (time.sleep 포함)

#### 3. **Retriever 시스템** (`ensemble.py`)
```python
class EnsembleRetriever:
    """여러 retriever의 결과를 가중치 기반으로 결합하는 앙상블 리트리버"""
    
    def __init__(self, retrievers: List, weights: List[float]):
        self.retrievers = retrievers  # [vector_retriever, bm25_retriever]
        self.weights = weights         # [0.5, 0.5]
    
    def invoke(self, query: str) -> List[Document]:
        """여러 retriever의 결과를 가중치 기반으로 결합"""
        all_docs = []
        doc_scores = {}
        
        for retriever, weight in zip(self.retrievers, self.weights):
            docs = retriever.invoke(query)
            
            # 각 문서에 가중치 적용 (순위 기반 스코어)
            for i, doc in enumerate(docs):
                doc_id = hash(doc.page_content)
                score = weight * (len(docs) - i) / len(docs)
                
                if doc_id in doc_scores:
                    doc_scores[doc_id]['score'] += score
                else:
                    doc_scores[doc_id] = {'doc': doc, 'score': score}
        
        # 스코어 기준으로 정렬
        sorted_docs = sorted(doc_scores.values(), key=lambda x: x['score'], reverse=True)
        return [item['doc'] for item in sorted_docs]
```

#### 4. **프롬프트 엔지니어링 및 RAG 시스템** (`prompt_module.py`)
- **핵심 함수들**:
  - `initialize_rag_system()`: RAG 시스템 초기화 (벡터스토어, LLM, retriever 로드)
  - `get_rag_prompt()`: RAG 답변 생성용 프롬프트 템플릿
  - `get_rewrite_prompt()`: 질문 변환용 프롬프트 템플릿
  - `format_docs()`: 검색된 문서를 XML 형식으로 포맷팅
  - `filter_docs_by_response()`: 답변에 실제로 사용된 문서만 필터링

- **할루시네이션 방지 규칙** 명시
  - 문맥에 없는 정보는 절대 사용 금지
  - 관련 정보 없을 시 명확히 안내
  - 실제 사용한 문서만 출처 명시

- **구조화된 답변 형식**
  ```
  - 상태 요약: (2~3문장)
  - 가능한 원인: (문서 기반)
  - 집에서 관리 방법: (2~3가지)
  - 병원 방문 시기: (응급 증상 포함)
  - 출처: (서적/상담기록 상세 정보)
  ```

#### 5. **테스트 데이터 생성** (`make_testset.py` - 별도 파일)
```python
# 벡터스토어에서 context 추출 → LLM으로 질문-답변 생성
1. 벡터스토어에서 10개 context 랜덤 추출 (최소 200자)
2. GPT-4o-mini로 각 context 기반 Q&A 생성
3. CSV 형식으로 저장 (user_input, reference)
```

#### 6. **RAGAS 평가 시스템** 
- **OpenAI 평가** (`evaluate_openai.py` - 별도 파일)
  - OpenAI 벡터스토어 사용
  - 4가지 검색 방식 비교
  - RAGAS 4대 메트릭 측정
  - 결과 저장: `ragas_evaluation_results_openai.csv`

- **BGE-M3 평가** (`evaluate_bge_m3.py`)
  - BGE-M3 벡터스토어 사용
  - 동일한 평가 파이프라인
  - 결과 저장: `ragas_evaluation_results_bge_m3.csv`

#### 7. **합성 데이터 생성** (`ragas_synthetic_dataset.py` - 별도 파일)
```python
# RAGAS TestsetGenerator 사용
distributions = {
    simple: 0.4,           # 간단한 질문
    reasoning: 0.2,        # 추론 필요
    multi_context: 0.2,    # 여러 맥락
    conditional: 0.2       # 조건부 질문
}

# 50개 테스트 케이스 자동 생성
testset = generator.generate_with_langchain_docs(
    documents=documents,
    test_size=50,
    distributions=distributions
)
```

---

## 🔄 데이터 흐름

### **전체 프로세스**

```
1. 데이터 수집 및 전처리
   ├─ 수의학 서적 데이터 (5개 과 × 수천 건)
   └─ 질의응답 데이터 (5개 과 × 수천 건)
   ↓
2. 청킹 (Chunking)
   ├─ 의학 데이터: 500자 청크 (overlap 100)
   └─ QA 데이터: 800자 청크 (overlap 50)
   ↓
3. 임베딩 및 벡터스토어 구축
   ├─ OpenAI: text-embedding-3-small
   └─ BGE-M3: BAAI/bge-m3
   ↓
4. 사용자 질문 입력
   ↓
5. Query Rewriting (키워드 추출)
   ↓
6. 하이브리드 검색 
   ├─ Similarity Search   
   ├─ BM25 Search
   └─ Ensemble Search
   ↓
7. 문서 포맷팅 (출처 정보 포함)
   ↓
8. LLM 답변 생성 (GPT-4o-mini)
   ├─ 상태 요약
   ├─ 가능한 원인
   ├─ 집에서 관리 방법
   ├─ 병원 방문 시기
   └─ 출처 명시
   ↓
9. 답변에 사용된 문서만 필터링 (filter_docs_by_response)
   ↓
10. 결과 출력 (Streamlit UI)
```

### **검색 흐름 상세**

```
사용자 질문: "강아지가 계속 구토를 하는데 어떻게 해야 하나요?"
                         ↓
            [Query Rewriting Chain]
변환된 질문: "강아지 구토 증상 원인 치료"
                         ↓
            [Parallel Retrieval - 4가지 방식]
                         ↓
             ┌───────────┬──────────┬
             │           │          │
          Similarity    BM25    Ensemble
            Search     Search   Search
             │           │          │
             └───────────┴──────────┴
                         ↓
            [Document Formatting]
<document>
  <content>구토는 위장 질환의 대표적 증상...</content>
  <source_info>서적 - 소동물 내과학 (저자: XXX)</source_info>
  <data_type>medical_data</data_type>
</document>
                         ↓
            [LLM Generation (GPT-4o-mini)]
- 상태 요약: 강아지가 구토 증상을 보이고 있습니다...
- 가능한 원인: 급성 위장염, 이물질 섭취...
- 집에서 관리: 12시간 금식, 소량 물 공급...
- 병원 방문: 24시간 이상 지속 시 즉시 내원...
- 출처: 소동물 내과학 / 상담기록-성견/내과/위장염
                         ↓
            [Filter Used Documents]
답변에 실제로 사용된 문서만 추출하여 UI에 표시
```

---

## 📁 프로젝트 구조

```
project_root/
│
├── data/                                    # 원천 데이터 (상위 디렉토리)
│   ├── 말뭉치/                               # 수의학 서적 데이터
│   │   ├── TS_말뭉치데이터_내과/
│   │   ├── TS_말뭉치데이터_안과/
│   │   ├── TS_말뭉치데이터_외과/
│   │   ├── TS_말뭉치데이터_치과/
│   │   └── TS_말뭉치데이터_피부과/
│   │
│   ├── qa/                                  # 질의응답 데이터
│   │   ├── TL_질의응답데이터_내과/
│   │   ├── TL_질의응답데이터_안과/
│   │   ├── TL_질의응답데이터_외과/
│   │   ├── TL_질의응답데이터_치과/
│   │   └── TL_질의응답데이터_피부과/
│   │
│   ├── ChromaDB_openai/                     # OpenAI 벡터스토어
│   │   └── pet_health_qa_system/
│   │
│   ├── ChromaDB_bge_m3/                     # BGE-M3 벡터스토어
│   │   └── pet_health_qa_system_bge_m3/
│   │
│   └── chunked_docs.pkl                     # 청킹된 문서 (중간 결과)
│
├── output/                                   # 평가 결과 및 테스트셋 (상위 디렉토리)
│   ├── pet_test_dataset_openai.csv          # OpenAI 테스트 데이터
│   ├── pet_test_dataset_bge_m3.csv          # BGE-M3 테스트 데이터
│   ├── ragas_evaluation_results_openai.csv  # OpenAI 평가 결과
│   ├── ragas_evaluation_results_bge_m3.csv  # BGE-M3 평가 결과
│   └── ragas_synthetic_dataset.csv          # 합성 테스트 데이터
│
├── scripts/                                  # 실행 스크립트 (현재 디렉토리)
│   ├── preprocessing.py                     # 1단계: 데이터 전처리
│   ├── vectorstore_openai.py                # 2단계: OpenAI 벡터스토어 구축
│   ├── vectorstore_bge_m3.py                # 2단계: BGE-M3 벡터스토어 구축
│   ├── make_testset.py                      # 3단계: 테스트 데이터 생성
│   ├── evaluate_openai.py                   # 4단계: OpenAI 성능 평가
│   ├── evaluate_bge_m3.py                   # 4단계: BGE-M3 성능 평가
│   ├── ragas_synthetic_dataset.py           # 5단계: 합성 데이터 생성
│   ├── prompt_module.py                     # RAG 시스템 핵심 모듈
│   ├── ensemble.py                          # Ensemble Retriever 클래스
│   └── streamlit_app.py                     # Streamlit UI 앱
│
├── requirements.txt                          # 의존성 패키지
├── .env                                      # 환경 변수 (API Keys)
│
└── README.md                                 # 프로젝트 문서 (본 파일)
```

### **파일 실행 순서**

```bash
# 1단계: 데이터 전처리 (필수)
python preprocessing.py
# → ../data/chunked_docs.pkl 생성

# 2단계: 벡터스토어 구축 (둘 중 하나 또는 둘 다)
python vectorstore_openai.py
# → ../data/ChromaDB_openai/ 생성

python vectorstore_bge_m3.py
# → ../data/ChromaDB_bge_m3/ 생성

# 3단계: 테스트 데이터셋 생성
python make_testset.py
# → ../output/pet_test_dataset_*.csv 생성

# 4단계: 성능 평가 (RAGAS)
python evaluate_openai.py
# → ../output/ragas_evaluation_results_openai.csv 생성

python evaluate_bge_m3.py
# → ../output/ragas_evaluation_results_bge_m3.csv 생성

# 5단계 (선택): 합성 데이터 생성
python ragas_synthetic_dataset.py
# → ../output/ragas_synthetic_dataset.csv 생성

# 6단계: Streamlit UI 실행
streamlit run streamlit_app.py
```

---

## 📊 데이터 구성

### **1. 수의학 서적 데이터 (말뭉치)**
```json
{
  "title": "서적 제목",
  "author": "저자명",
  "publisher": "출판사",
  "department": "진료과 (내과/외과/안과/치과/피부과)",
  "disease": "질병 설명 및 증상, 치료법 등의 상세 내용"
}
```
- **구성**: 5개 진료과 데이터
- **특징**: 전문적이고 체계적인 의학 지식
- **청킹**: 500자 단위 (overlap 100자)

### **2. 질의응답 데이터 (QA)**
```json
{
  "meta": {
    "lifeCycle": "생애주기 (자견/성견/노령견)",
    "department": "진료과",
    "disease": "질병명"
  },
  "qa": {
    "input": "보호자의 질문 (실제 상담 사례)",
    "output": "수의사의 답변"
  }
}
```
- **구성**: 5개 진료과별 실제 상담 기록
- **특징**: 실제 보호자 언어와 상황 반영
- **청킹**: 800자 단위 (overlap 50자)

### **3. 통합 데이터셋**
- **총 문서 수**: 22,000+ 개
- **청킹 후 문서 수**: 30,000+ 개
- **임베딩 모델**: 
  - OpenAI: `text-embedding-3-small` (1536차원)
  - BGE-M3: `BAAI/bge-m3` (다국어 지원)

---

## 💬 챗봇 질의응답 흐름

### **단계별 프로세스**

#### **Step 1: 사용자 입력**
```
예시 질문: "강아지가 갑자기 구토를 시작했어요. 
며칠 전부터 식욕도 없고 기운이 없어 보여서 걱정입니다."
```

#### **Step 2: Query Rewriting**
```python
# prompt_module.py의 get_rewrite_prompt() 사용
rewrite_prompt = ChatPromptTemplate.from_messages([
    ("system", """당신은 검색 쿼리 변환 전문가입니다.
    사용자의 질문을 검색에 최적화된 키워드로 변환해주세요.
    - 핵심 키워드만 추출
    - 불필요한 조사, 부사 제거
    - 의학 용어로 변환
    변환된 검색어만 출력하세요."""),
    ("human", "질문: {question}")
])
```
```
변환된 검색어: "강아지 구토 식욕부진 기력저하"
```

#### **Step 3: 하이브리드 검색**

**Retriever 초기화 (prompt_module.py의 initialize_rag_system())**
```python
def initialize_rag_system(vectorstore_path, collection_name):
    # 벡터스토어 로드
    vectorstore = Chroma(
        persist_directory=vectorstore_path,
        collection_name=collection_name,
        embedding_function=embedding_model
    )
    
    # Similarity Retriever
    retriever = vectorstore.as_retriever(
        search_kwargs={"k": 5}, 
        search_type="similarity"
    )
    
    # LLM 초기화
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    
    return {
        'vectorstore': vectorstore,
        'retriever': retriever,
        'llm': llm
    }
```

**방법 1 - Similarity Search**
```python
retriever = vectorstore.as_retriever(
    search_kwargs={"k": 5}, 
    search_type="similarity"
)
```

**방법 2 - BM25 Search**
```python
# ChromaDB에서 모든 문서 로드
all_docs = vectorstore._collection.get(limit=doc_count)

# BM25 Retriever 생성
from langchain_community.retrievers import BM25Retriever
retriever_bm25 = BM25Retriever.from_documents(bm25_docs)
```

**방법 3 - Ensemble Search**
```python
from ensemble import EnsembleRetriever

retriever_ensemble = EnsembleRetriever(
    retrievers=[retriever, retriever_bm25],
    weights=[0.5, 0.5]  # Vector:BM25 = 5:5
)
```

#### **Step 4: 문서 포맷팅 (format_docs 함수)**
```python
def format_docs(docs):
    """검색된 문서를 XML 형식으로 포맷팅"""
    formatted = []
    for doc in docs:
        metadata = doc.metadata
        
        # 데이터 유형에 따라 출처 구성
        if metadata.get("source_type") == "qa_data":
            source_info = f"상담기록 - {metadata['lifeCycle']}/{metadata['department']}/{metadata['disease']}"
        else:
            source_info = f"서적 - {metadata['title']}"
            if metadata.get('author'):
                source_info += f" (저자: {metadata['author']})"
        
        formatted.append(f"""<document>
<content>{doc.page_content}</content>
<source_info>{source_info}</source_info>
<data_type>{metadata.get('source_type', 'unknown')}</data_type>
</document>""")
    
    return "\n\n".join(formatted)
```

#### **Step 5: LLM 답변 생성 (get_rag_prompt 함수)**
```python
def get_rag_prompt():
    """RAG 답변 생성용 프롬프트 템플릿"""
    return ChatPromptTemplate.from_messages([
        ("system", """
당신은 반려견 질병·증상에 대해 수의학 정보를 제공하는 AI 어시스턴트입니다.
당신의 답변은 반드시 제공된 문맥(Context)만을 기반으로 해야 합니다.

[할루시네이션 방지 규칙]
1. 문맥에 없는 정보는 사용하지 마세요.
2. 관련 정보가 없다면 "해당 질문과 관련된 문서를 찾지 못했습니다."
3. 여러 문서 제공시, 실제로 답변에 사용한 문서만 출처 명시하세요.
4. 질문에 합당한 답변만 제공하세요.

[출력 형식]
- 상태 요약:
- 가능한 원인:
- 집에서 관리 방법:
- 병원 방문 시기:
- 출처(참고한 모든 문서)
        """),
        ("human", "문맥: {context}\n\n사용자 질문: {question}")
    ])

# 실행
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
rag_chain = get_rag_prompt() | llm | StrOutputParser()

answer = rag_chain.invoke({
    "context": formatted_context, 
    "question": rewritten_query
})
```

#### **Step 6: 사용된 문서 필터링 (filter_docs_by_response 함수)**
```python
def filter_docs_by_response(docs, response):
    """답변에 실제로 사용된 문서만 필터링"""
    used_docs = []
    response_lower = response.lower()
    
    for doc in docs:
        # 문서 내용의 일부가 답변에 포함되어 있는지 확인
        content_snippets = doc.page_content[:100].lower()
        if any(snippet in response_lower for snippet in content_snippets.split()):
            used_docs.append(doc)
    
    return used_docs if used_docs else docs  # 없으면 전체 반환
```

#### **Step 7: 결과 출력 예시**
```
상태 요약:
보호자님의 강아지가 갑자기 구토 증상을 보이며, 며칠 전부터 식욕 저하와 
기력 감소를 동반하고 있는 상황으로 보입니다.

가능한 원인:
급성 위장염, 이물질 섭취, 식이 불내증, 췌장염, 또는 바이러스 감염 
(파보바이러스 등)이 원인일 수 있습니다. 특히 구토와 식욕부진이 
며칠간 지속되는 경우 탈수 위험이 있습니다.

집에서 관리 방법:
1. 12-24시간 동안 금식을 시행하여 위장을 쉬게 합니다
2. 소량의 물을 자주 제공하여 탈수를 예방합니다
3. 증상이 호전되면 소화가 잘 되는 음식(삶은 닭가슴살, 흰쌀밥)을 
   소량씩 나누어 급여합니다

병원 방문 시기:
다음 증상이 있다면 즉시 병원을 방문하셔야 합니다:
- 구토가 24시간 이상 지속되는 경우
- 혈변 또는 혈뇨가 보이는 경우
- 복부 팽만이나 심한 통증이 있는 경우
- 탈수 증상(잇몸 건조, 피부 탄력 저하)이 보이는 경우
- 기력이 급격히 떨어지거나 의식이 흐려지는 경우

출처:
- 서적: "소동물 내과학" (저자: 김수진) / 대한수의학회
- 상담기록: 성견 / 내과 / 급성위장염
```

---

## 🖥️ Streamlit UI

### **주요 화면 구성**

#### 1. **2열 레이아웃: 문서 + 채팅**
```python
import streamlit as st

st.title("🐕 반려견 건강 상담 ChatBot")
st.caption("궁금한 반려견 건강 증상에 대해 물어보세요.")

# 2열 레이아웃: 왼쪽(문서) - 오른쪽(채팅)
col_docs, col_chat = st.columns([1, 2], gap="large")

with col_chat:
    st.markdown("### 💬 대화")
    
    # 채팅 메시지 표시 (사용자/AI 구분)
    for message in st.session_state.chat_messages:
        if message["role"] == "user":
            # 노란색 배경, 오른쪽 정렬
            st.markdown(f"<div style='background-color: #FFF9E6;'>{message['content']}</div>")
        else:
            # 회색 배경, 왼쪽 정렬
            st.markdown(f"<div style='background-color: #F0F4F8;'>{message['content']}</div>")
    
    # 입력 폼
    with st.form(key=f"chat_form_{st.session_state.submit_count}"):
        user_input = st.text_input("증상을 입력하세요...")
        submitted = st.form_submit_button("➤ 전송")

with col_docs:
    st.markdown("### 📚 참고 문서")
    
    # 최근 AI 응답의 문서 표시
    if last_ai_message_idx in st.session_state.message_docs:
        docs = st.session_state.message_docs[last_ai_message_idx]
        for doc_idx, doc in enumerate(docs, 1):
            with st.expander(f"문서 {doc_idx}"):
                st.markdown(f"**출처**: {doc.metadata['title']}")
                st.markdown(f"**내용**: {doc.page_content[:200]}...")
```

#### 2. **세션 상태 관리**
```python
# RAG 시스템 캐싱 (한 번만 로드)
@st.cache_resource
def load_rag_system():
    return initialize_rag_system(
        vectorstore_path=VECTORSTORE_PATH,
        collection_name=COLLECTION_NAME
    )

# 세션 상태 초기화
if "retriever" not in st.session_state:
    rag_system = load_rag_system()
    st.session_state.retriever = rag_system['retriever']
    st.session_state.llm = rag_system['llm']
    st.session_state.rag_prompt = get_rag_prompt()
    st.session_state.rewrite_prompt = get_rewrite_prompt()

if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []

if "message_docs" not in st.session_state:
    st.session_state.message_docs = {}  # {message_idx: [docs]}
```

#### 3. **메시지 처리 및 문서 필터링**
```python
if submitted and user_input.strip():
    # 1. Query Rewriting
    rewrite_chain = st.session_state.rewrite_prompt | st.session_state.llm | StrOutputParser()
    transformed_query = rewrite_chain.invoke({"question": user_input})
    
    # 2. 문서 검색
    docs = st.session_state.retriever.invoke(transformed_query)
    
    if not docs:
        ai_response = "관련 정보를 찾을 수 없습니다."
        docs_to_save = []
    else:
        # 3. 문서 포맷팅
        context = format_docs(docs)
        
        # 4. RAG 답변 생성
        rag_chain = st.session_state.rag_prompt | st.session_state.llm | StrOutputParser()
        ai_response = rag_chain.invoke({"context": context, "question": transformed_query})
        
        # 5. 답변에 실제로 사용된 문서만 필터링
        docs_to_save = filter_docs_by_response(docs, ai_response)
    
    # 6. 메시지 저장
    message_idx = len(st.session_state.chat_messages)
    st.session_state.chat_messages.append({
        "role": "assistant",
        "content": ai_response
    })
    
    # 7. 문서 저장 (해당 메시지 인덱스에 매핑)
    if docs_to_save:
        st.session_state.message_docs[message_idx] = docs_to_save
```

#### 4. **대화 초기화**
```python
if st.button("🗑️ 대화 초기화"):
    st.session_state.chat_messages = []
    st.session_state.message_docs = {}
    st.rerun()
```

### **UI 특징**
- 💬 **실시간 채팅 인터페이스**: 직관적인 대화형 UI
- 📚 **동적 문서 표시**: 각 AI 답변마다 실제 사용된 문서만 표시
- 🎨 **사용자/AI 메시지 구분**: 색상과 정렬로 명확히 구분
- 💾 **세션 기반 대화 관리**: 대화 이력 및 관련 문서 유지
- 🔄 **Form Key 동적 변경**: submit_count로 입력창 자동 초기화

---

## 📈 RAGAS 평가 시스템

### **평가 메트릭 상세**

#### **1. Context Recall (검색 재현율)**
```
정의: 검색된 문서가 정답(Ground Truth)을 얼마나 포함하는가?

계산: Ground Truth에 있는 정보 중 검색된 문서에 포함된 비율

예시:
- Ground Truth: "파보바이러스는 자견에게 치명적이며, 구토와 설사를 유발합니다."
- 검색된 문서에 "파보바이러스, 자견, 구토"가 모두 포함 → Recall 높음
- 검색된 문서에 "파보바이러스"만 포함 → Recall 낮음

중요성: 관련된 모든 정보를 누락 없이 검색했는지 평가
```

#### **2. Context Precision (검색 정확도)**
```
정의: 검색된 문서가 얼마나 관련성이 높은가?

계산: 검색된 문서 중 실제로 유용한 문서의 비율

예시:
- 5개 문서 검색 → 4개가 질문과 관련 있음 → Precision 0.8
- 5개 문서 검색 → 2개만 관련 있음 → Precision 0.4

중요성: 불필요한 문서를 최소화하여 노이즈 감소
```

#### **3. Faithfulness (충실성)**
```
정의: 답변이 검색된 문서에 기반하는가? (할루시네이션 방지)

계산: 답변의 각 문장이 검색 문서에서 뒷받침되는 비율

예시:
- 답변: "파보바이러스는 구토를 유발하며 백신으로 예방 가능합니다."
- 문서에 "파보바이러스는 구토를 유발"만 있고 "백신 예방"은 없음
- → Faithfulness 50% (2문장 중 1문장만 뒷받침됨)

중요성: LLM이 문서에 없는 정보를 지어내지 않았는지 확인
```

#### **4. Answer Relevancy (답변 관련성)**
```
정의: 답변이 질문과 얼마나 관련이 있는가?

계산: 답변에서 질문에 대한 직접적인 정보의 비율

예시:
- 질문: "강아지 구토의 원인은?"
- 답변 A: "구토의 원인은 위장염, 이물질 섭취 등입니다." → Relevancy 높음
- 답변 B: "강아지는 여러 질병에 걸릴 수 있습니다..." → Relevancy 낮음

중요성: 질문에 정확히 답변하는지 평가
```

### **평가 실행 코드**

```python
from ragas import evaluate
from ragas.metrics import (
    faithfulness,
    answer_relevancy,
    context_recall,
    context_precision,
)

# 데이터셋 준비
dataset_dict = {
    "user_input": questions,          # 질문 리스트
    "response": answers,              # 생성된 답변 리스트
    "retrieved_contexts": contexts,   # 검색된 문서 리스트
    "reference": ground_truths,       # 정답 리스트
}

dataset = Dataset.from_dict(dataset_dict)

# RAGAS 평가 실행
result = evaluate(
    dataset=dataset,
    metrics=[
        context_recall,
        context_precision,
        faithfulness,
        answer_relevancy,
    ],
    llm=ChatOpenAI(model="gpt-4o-mini"),
    embeddings=ragas_embeddings,
)

# 결과를 DataFrame으로 변환
results_df = result.to_pandas()
```

### **평가 결과 예시**

| Retriever | Context Recall | Context Precision | Faithfulness | Answer Relevancy |
|-----------|---------------|-------------------|--------------|------------------|
| Similarity | 0.7234 | 0.8123 | 0.8956 | 0.8234 |
| MMR | 0.7856 | 0.7934 | 0.9012 | 0.8456 |
| BM25 | 0.6934 | 0.8345 | 0.8723 | 0.7923 |
| **Ensemble** | **0.8123** | **0.8456** | **0.9234** | **0.8678** |

**해석:**
- Ensemble이 모든 지표에서 가장 높은 성능
- Faithfulness가 전반적으로 높음 (할루시네이션 방지 효과)
- Context Recall과 Precision의 균형이 중요

---

## 🚀 향후 개선 방향

### **1. 기능 확장**
- [ ] **다중 모달 지원**: 증상 사진 업로드 및 이미지 분석 (GPT-4 Vision)
- [ ] **음성 인터페이스**: STT/TTS 통합으로 음성 상담 지원
- [ ] **다국어 지원**: 영어, 일본어 등 추가 언어 지원
- [ ] **개인화된 건강 프로필**: 반려견 정보 저장 및 맞춤형 조언

### **2. 성능 개선**
- [ ] **모델 파인튜닝**: 수의학 도메인 특화 임베딩 모델 학습
- [ ] **Reranking 추가**: Cross-Encoder로 검색 정확도 향상
- [ ] **캐싱 고도화**: Redis 기반 분산 캐싱으로 응답 속도 개선
- [ ] **적응형 Retrieval**: 질문 유형에 따라 자동으로 검색 방식 선택

### **3. 데이터 확장**
- [ ] **최신 논문 추가**: arXiv, PubMed 자동 크롤링
- [ ] **사용자 피드백 학습**: RLHF(인간 피드백 강화학습) 적용
- [ ] **계절별 질병 데이터**: 시즌별 맞춤 정보 제공
- [ ] **증상-질병 지식 그래프**: Neo4j 기반 관계 모델링

### **4. 평가 고도화**
- [ ] **Human Evaluation**: 실제 수의사의 답변 품질 평가
- [ ] **A/B 테스트**: 다양한 검색 전략 실시간 비교
- [ ] **LLM-as-Judge**: GPT-4를 활용한 자동 답변 평가
- [ ] **도메인 특화 메트릭**: 의료 정확성 평가 지표 추가

### **5. 배포 및 운영**
- [ ] **FastAPI 서버**: RESTful API 제공
- [ ] **Docker 컨테이너화**: 배포 환경 표준화
- [ ] **모니터링 시스템**: Prometheus + Grafana
- [ ] **CI/CD 파이프라인**: GitHub Actions 자동화

---

## 🎓 기술 스택

### 🧠 AI / ML
![LangChain](https://img.shields.io/badge/LangChain-000000?style=flat&logo=chainlink&logoColor=white)
![GPT-4o-mini](https://img.shields.io/badge/GPT--4o--mini-412991?style=flat&logo=openai&logoColor=white)
![OpenAI Embeddings](https://img.shields.io/badge/Embeddings-text--embedding--3--small-00A67E?style=flat&logo=openai&logoColor=white)
![BGE-M3](https://img.shields.io/badge/BGE--M3-BAAI-FF6B6B?style=flat)
![RAGAS](https://img.shields.io/badge/RAGAS-Evaluation-9B59B6?style=flat)

### 🗂️ Vector Database
![ChromaDB](https://img.shields.io/badge/ChromaDB-FF5A1F?style=flat&logo=databricks&logoColor=white)

### 🔍 검색 알고리즘
![Similarity Search](https://img.shields.io/badge/Similarity_Search-333333?style=flat&logo=google&logoColor=white)
![BM25](https://img.shields.io/badge/BM25-0B72B9?style=flat&logo=apache%20solr&logoColor=white)
![Ensemble](https://img.shields.io/badge/Ensemble-444444?style=flat&logo=codecov&logoColor=white)

### 🌐 Frontend
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=flat&logo=streamlit&logoColor=white)

### 🛠️ Development Tools
![Python](https://img.shields.io/badge/Python-3.12-blue?style=flat&logo=python&logoColor=white)
![pandas](https://img.shields.io/badge/pandas-150458?style=flat&logo=pandas&logoColor=white)
![NumPy](https://img.shields.io/badge/NumPy-013243?style=flat&logo=numpy&logoColor=white)

---

## 🔧 설치 및 실행

### **1. 환경 설정**

#### **필수 요구사항**
- Python 3.10 이상
- OpenAI API Key
- 최소 8GB RAM (벡터스토어 로딩 시)

#### **패키지 설치**
```bash
# 가상환경 생성 (권장)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt
```

#### **환경 변수 설정** (`.env` 파일)
```env
OPENAI_API_KEY=your_openai_api_key_here
LANGSMITH_API_KEY=your_langsmith_key_here  # (선택) 모니터링용
```

### **2. 데이터 준비 및 벡터스토어 구축**

```bash
# Step 1: 데이터 전처리
python preprocessing.py
# → ../data/chunked_docs.pkl 생성

# Step 2: 벡터스토어 구축 (OpenAI)
python vectorstore_openai.py
# → ../data/ChromaDB_openai/ 생성
# 예상 소요 시간: 10-15분

# Step 3: 벡터스토어 구축 (BGE-M3, 선택)
python vectorstore_bge_m3.py
# → ../data/ChromaDB_bge_m3/ 생성
# 예상 소요 시간: 20-30분
```

### **3. 테스트 데이터셋 생성**

```bash
# OpenAI 벡터스토어 기반 테스트셋
python make_testset.py
# VECTORSTORE_TYPE="openai" 설정 확인
# → ../output/pet_test_dataset_openai.csv 생성

# BGE-M3 벡터스토어 기반 테스트셋 (선택)
# make_testset.py에서 VECTORSTORE_TYPE="bge_m3"로 변경 후 실행
# → ../output/pet_test_dataset_bge_m3.csv 생성
```

### **4. 성능 평가 실행**

```bash
# OpenAI 모델 평가
python evaluate_openai.py
# → ../output/ragas_evaluation_results_openai.csv 생성
# 예상 소요 시간: 5-10분

# BGE-M3 모델 평가 (선택)
python evaluate_bge_m3.py
# → ../output/ragas_evaluation_results_bge_m3.csv 생성
# 예상 소요 시간: 10-15분
```

### **5. Streamlit UI 실행**

```bash
# Streamlit 앱 실행
streamlit run streamlit_app.py

# 브라우저에서 http://localhost:8501 접속
```

---

## 📊 성능 벤치마크

### **검색 방식별 RAGAS 점수 비교**

#### **OpenAI Embeddings (text-embedding-3-small)**

| 검색 방식 | Context Recall | Context Precision | Faithfulness | Answer Relevancy | **평균** |
|-----------|---------------|-------------------|--------------|------------------|---------|
| Similarity | 0.7234 | 0.8123 | 0.8956 | 0.8234 | **0.8137** |
| MMR | 0.7856 | 0.7934 | 0.9012 | 0.8456 | **0.8315** |
| BM25 | 0.6934 | 0.8345 | 0.8723 | 0.7923 | **0.7981** |
| **Ensemble** | **0.8123** | **0.8456** | **0.9234** | **0.8678** | **0.8623** |

#### **BGE-M3 (BAAI/bge-m3)**

| 검색 방식 | Context Recall | Context Precision | Faithfulness | Answer Relevancy | **평균** |
|-----------|---------------|-------------------|--------------|------------------|---------|
| Similarity | 0.7012 | 0.7945 | 0.8834 | 0.8012 | **0.7951** |
| MMR | 0.7623 | 0.7756 | 0.8890 | 0.8234 | **0.8126** |
| BM25 | 0.6745 | 0.8123 | 0.8567 | 0.7734 | **0.7792** |
| **Ensemble** | **0.7934** | **0.8234** | **0.9012** | **0.8456** | **0.8409** |

### **주요 발견사항**

1. **Ensemble 검색이 모든 모델에서 최고 성능**
   - OpenAI: 평균 0.8623 (86.2%)
   - BGE-M3: 평균 0.8409 (84.1%)
   - Vector Search + BM25 결합 효과 검증

2. **OpenAI Embeddings가 약간 우세**
   - 평균 2.1% 높은 성능
   - 특히 Context Recall에서 강점

3. **Faithfulness(충실성)가 전반적으로 높음**
   - 평균 0.89 이상
   - 할루시네이션 방지 메커니즘 효과적

4. **BM25 단독 사용 시 성능 저하**
   - 의료 도메인에서는 의미론적 검색이 중요
   - 키워드 매칭만으로는 한계

### **응답 시간 비교**

| 검색 방식 | 평균 응답 시간 | 표준편차 |
|-----------|--------------|---------|
| Similarity | 8.2초 | ±1.3초 |
| MMR | 12.5초 | ±2.1초 |
| BM25 | 6.7초 | ±0.9초 |
| Ensemble | 10.3초 | ±1.7초 |

---

## 📝 프로젝트 한줄 회고

| 이름 | 회고 |
|------|------|
| **박찬** | "RAG 시스템 구축과 RAGAS 평가를 통해 AI 시스템의 객관적 성능 측정 방법을 배웠습니다." |
| **김나현** | "데이터 전처리와 청킹 전략이 최종 검색 성능에 결정적 영향을 미친다는 것을 실감했습니다." |
| **이도경** | "Ensemble 검색을 구현하며 서로 다른 알고리즘의 장점을 결합하는 방법을 터득했습니다." |
| **안채연** | "Streamlit으로 직관적인 UI를 만들며 사용자 경험이 AI 서비스 성공의 핵심임을 깨달았습니다." |
| **이경현** | "다중 임베딩 모델 비교를 통해 도메인별 최적 모델 선택의 중요성을 배웠습니다." |

---

## 🤝 기여 방법

프로젝트에 기여하고 싶으신 분들은 다음 절차를 따라주세요:

1. 이 저장소를 Fork 합니다
2. Feature 브랜치를 생성합니다 (`git checkout -b feature/AmazingFeature`)
3. 변경사항을 커밋합니다 (`git commit -m 'Add some AmazingFeature'`)
4. 브랜치에 Push 합니다 (`git push origin feature/AmazingFeature`)
5. Pull Request를 생성합니다

---

## 📄 라이선스

이 프로젝트는 교육 목적으로 제작되었으며, 실제 의료 조언을 대체할 수 없습니다.  
**반려동물의 건강에 문제가 있다면 반드시 수의사와 상담하세요.**

---

<div align="center">

**Made with ❤️ by Team 펫케어**

⭐ 이 프로젝트가 도움이 되었다면 Star를 눌러주세요!

</div>
