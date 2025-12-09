# 🐕 LLM을 연동한 내외부 문서 기반 질의응답 시스템

**강아지 질병 증상 상담 챗봇**

---

## 👥 팀원 소개

| 이름 | 역할 |
|------|------|
| **박찬** | 팀장 |
| **김나현** | 팀원 |
| **이도경** | 팀원 |
| **안채연** | 팀원 |
| **이경현** | 팀원 |

---

## 📌 프로젝트 개요

### **강아지 질병 증상 챗봇**

반려견 보호자가 강아지의 증상을 입력하면, AI가 수의학 지식 데이터베이스와 과거 상담 기록을 기반으로 정확한 의료정보를 제공하는 Chat-bot입니다.

### **주요 특징**
- 📚 **30,000+ 건의 수의학 데이터** 기반 정확한 답변
- 🔍 **3단계 하이브리드 검색** (Threshold → MMR → Ensemble)
- 💬 **Streamlit 기반 직관적인 UI**
- 🎯 **할루시네이션 방지 메커니즘** 적용

---

## 🎯 개발 동기

### **문제 인식**
1. **정보 접근성 문제**: 반려견 보호자들이 증상 발생 시 신뢰할 수 있는 정보를 찾기 어려움
2. **응급 상황 판단 어려움**: 어떤 증상이 응급인지, 언제 병원에 가야 하는지 판단이 어려움

### **해결 방안**
- **LLM + RAG 기술**을 활용하여 수의학 전문 지식을 기반으로 한 정확한 상담 제공
- **다단계 검색 시스템**으로 관련성 높은 정보만 선별하여 할루시네이션 최소화
---

## ⚡ 주요 기능

### 1. **증상 기반 질의응답**
- 반려견의 증상을 자연어로 입력하면 AI가 ChromaDB에 있는 데이터를 분석하여 답변 제공
- 가능한 원인, 집에서의 관리 방법, 병원 방문 시기 등을 종합적으로 안내

### 2. **3단계 하이브리드 검색 시스템**
```
1단계: Threshold Filtering
   ↓ (유사도 임계값 0.6 이상 필터링)
2단계: MMR (Maximal Marginal Relevance)
   ↓ (유사도 + 다양성 확보)
3단계: Ensemble (Vector + BM25)
   ↓ (의미론적 + 키워드 검색 결합)
최종 문서 선정
```

### 3. **할루시네이션 방지 메커니즘**
- 검색된 문서만을 기반으로 답변 생성
- 출처가 명확하지 않은 정보는 제공하지 않음
- 문서에 없는 정보 요청 시 명확히 안내

### 4. **대화 기록 관리**
- 이전 대화 내용 저장 및 불러오기
- 증상 변화 추적 가능
- 다중 세션 관리

---

## 🏗️ 시스템 아키텍처

```
┌─────────────────────────────────────────────────────────────┐
│                        사용자 인터페이스                         │
│                      (Streamlit UI)                           │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                      질의 응답 시스템                            │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────┐      ┌──────────────┐      ┌───────────┐ │
│  │  Query       │─────▶│  Retriever   │─────▶│   LLM     │ │
│  │  Processing  │      │  (3 Stages)  │      │ (GPT-4o)  │ │
│  └──────────────┘      └──────────────┘      └───────────┘ │
│         │                     │                      │      │
│         ▼                     ▼                      ▼      │
│  ┌──────────────┐      ┌──────────────┐      ┌───────────┐ │
│  │  Rewrite     │      │  Threshold   │      │  Prompt   │ │
│  │  Chain       │      │  MMR         │      │  Template │ │
│  └──────────────┘      │  Ensemble    │      └───────────┘ │
│                        └──────────────┘                     │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                      데이터 레이어                              │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────────┐                                       │
│  │  ChromaDB        │                                       │
│  │  (Vector Store)  │                                       │
│  │  30,000+ docs    │                                       │
│  └──────────────────┘                                       │
│                                                             │
│  - 수의학 서적 데이터                                         │
│  - 질의응답 데이터                                           │
│  - OpenAI Embeddings (text-embedding-3-small)                │
└─────────────────────────────────────────────────────────────┘
```

### **핵심 컴포넌트**

#### 1. **데이터 전처리 모듈** (`data_preprocessing.py`)
- 수의학 서적 데이터와 QA 데이터 통합
- 데이터 타입별 차별화된 청킹 전략
  - 의학 데이터: `chunk_size=500`, `chunk_overlap=100`
  - QA 데이터: `chunk_size=800`, `chunk_overlap=50`

#### 2. **벡터스토어 구축** (`vectorstore.py`)
- ChromaDB를 사용한 벡터 저장소 구축
- OpenAI Embeddings (text-embedding-3-small) 사용
- 배치 처리를 통한 대용량 데이터 효율적 임베딩

#### 3. **Retriever 시스템** (`retriever.py`)
- **1단계 - Threshold Filtering**: 유사도 임계값 기반 필터링
- **2단계 - MMR**: 유사도와 다양성을 동시에 고려
- **3단계 - Ensemble**: Vector Search + BM25 결합
- 문서 캐싱을 통한 성능 최적화

#### 4. **프롬프트 엔지니어링** (`prompt.py`, `prompt_new.py`)
- 할루시네이션 방지 규칙 적용
- 수의사 상담 톤의 자연스러운 응답 생성
- 출처 명시 및 구조화된 답변 형식

---

## 🔄 데이터 흐름

```
1. 사용자 질문 입력
   ↓
2. Query Rewriting (키워드 최적화)
   ↓
3. 3단계 하이브리드 검색
   ├─ Threshold Filtering (유사도 > 0.6)
   ├─ MMR (다양성 확보)
   └─ Ensemble (Vector + BM25)
   ↓
4. 문서 포맷팅 (출처 정보 포함)
   ↓
5. LLM 답변 생성 (GPT-4o-mini)
   ├─ 상태 요약
   ├─ 가능한 원인
   ├─ 집에서 관리 방법
   ├─ 병원 방문 시기
   └─ 출처 명시
   ↓
6. 결과 출력 (Streamlit UI)

```

---

## 📁 프로젝트 구조

```
project_root/
│
├── data/                          # 원천 데이터
│   ├── 말뭉치/                     # 수의학 서적 데이터
│   │   ├── TS_말뭉치데이터_내과/
│   │   ├── TS_말뭉치데이터_안과/
│   │   ├── TS_말뭉치데이터_외과/
│   │   ├── TS_말뭉치데이터_치과/
│   │   └── TS_말뭉치데이터_피부과/
│   │
│   └── qa/                        # 질의응답 데이터
│       ├── TL_질의응답데이터_내과/
│       ├── TL_질의응답데이터_안과/
│       ├── TL_질의응답데이터_외과/
│       ├── TL_질의응답데이터_치과/
│       └── TL_질의응답데이터_피부과/
│
├── ChromaDB/                      # 벡터 데이터베이스
│   └── pet_health_qa_system/      # 컬렉션
│
├── data_preprocessing.py          # 데이터 전처리 및 청킹
├── vectorstore.py                 # 벡터스토어 구축
├── retriever.py                   # 검색 시스템 (3단계)
├── prompt.py                      # 프롬프트 템플릿 및 체인
├── prompt_new.py                  # 개선된 프롬프트
├── test_retriever.py              # 검색 시스템 테스트
│
├── chunked_docs.pkl               # 청킹된 문서 (중간 결과)
├── requirements.txt               # 의존성 패키지
├── .env                           # 환경 변수 (API Keys)
│
└── README.md                      # 프로젝트 문서 (본 파일)
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

### **통합 데이터셋**
- **총 문서 수**: 22,000+ 개
- **청킹 후 문서 수**: 30,000+ 개
- **임베딩 모델**: OpenAI `text-embedding-3-small`
- **벡터 차원**: 1536 차원

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
# 원본 질문을 검색에 최적화된 형태로 변환
rewrite_prompt = PromptTemplate(
    "다음 질문을 검색에 더 적합한 형태로 변환해 주세요.
     키워드 중심으로 명확하게 바꿔주세요"
)
```
```
변환된 검색어: "강아지 구토 식욕부진 기력저하"
```

#### **Step 3: 3단계 검색**

**1단계 - Threshold Filtering**
```python
def threshold_retriever(query, threshold=0.6, k=10):
    # 유사도 0.6 이상인 문서만 선택
    results = vectorstore.similarity_search_with_score(query, k=k*2)
    filtered_docs = [doc for doc, score in results if score <= threshold]
    return filtered_docs[:k]
```

**2단계 - MMR (Maximal Marginal Relevance)**
```python
def mmr_retriever(query, threshold=0.6, k=10, lambda_mult=0.5):
    # 유사도와 다양성을 동시에 고려
    mmr_docs = vectorstore.max_marginal_relevance_search(
        query, k=k, fetch_k=k*2, lambda_mult=0.5
    )
    # threshold 필터링 적용
    return filtered_docs
```

**3단계 - Ensemble (Vector + BM25)**
```python
def ensemble_retriever(query, vector_weight=0.5, bm25_weight=0.5):
    # 벡터 검색 (의미론적)
    vector_docs = vectorstore.similarity_search(query, k=k)
    
    # BM25 검색 (키워드 기반)
    bm25_docs = bm25_retriever.invoke(query)
    
    # 가중치 기반 결합
    ensemble = EnsembleRetriever([vector_retriever, bm25_retriever],
                                  weights=[0.5, 0.5])
    return ensemble.invoke(query)
```

#### **Step 4: 문서 포맷팅**
```python
def format_docs(docs):
    formatted = []
    for doc in docs:
        source_info = (
            f"서적 - {doc.metadata['title']}" if doc.metadata['source_type'] == 'medical_data'
            else f"상담기록 - {doc.metadata['lifeCycle']}/{doc.metadata['department']}"
        )
        formatted.append(f"<document>
<content>{doc.page_content}</content>
<source_info>{source_info}</source_info>
</document>")
    return "\n\n".join(formatted)
```

#### **Step 5: LLM 답변 생성**
```python
prompt = ChatPromptTemplate.from_messages([
    ("system", """
    당신은 반려견 질병·증상에 대해 수의학 정보를 제공하는 AI 어시스턴트입니다.
    당신의 답변은 반드시 제공된 문맥(Context)만을 기반으로 해야 합니다.
    
    [할루시네이션 방지 규칙]
    1. 문맥에 없는 정보는 사용하지 마세요.
    2. 관련 정보가 없다면 "해당 질문과 관련된 문서를 찾지 못했습니다."
    3. 실제로 답변에 사용한 문서만 출처 명시
    
    [출력 형식]
    - 상태 요약:
    - 가능한 원인:
    - 집에서 관리 방법:
    - 병원 방문 시기:
    - 출처(참고한 모든 문서)
    """),
    ("human", "문맥: {context}\n\n사용자 질문: {question}")
])

rag_chain = prompt | llm | StrOutputParser()
answer = rag_chain.invoke({"context": context, "question": query})
```

#### **Step 6: 결과 출력 예시**
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

#### 1. **메인 대화 화면**
```python
import streamlit as st

st.title("🐕 강아지 건강 상담 챗봇")
st.caption("반려견의 증상을 입력하시면 AI가 수의학 정보를 제공합니다.")

# 채팅 인터페이스
user_input = st.chat_input("증상이나 궁금한 점을 입력해주세요...")

if user_input:
    with st.chat_message("user"):
        st.write(user_input)
    
    with st.chat_message("assistant"):
        with st.spinner("답변을 생성하고 있습니다..."):
            answer = get_answer(user_input, stage=3, k=5)
            st.write(answer)
```

#### 2. **병원 추천 화면**
```python
if st.button("🏥 근처 동물병원 찾기"):
    with st.spinner("병원을 검색하고 있습니다..."):
        hospitals = search_nearby_hospitals(location)
        
        for hospital in hospitals:
            with st.expander(f"📍 {hospital['name']}"):
                st.write(f"**주소**: {hospital['address']}")
                st.write(f"**전화번호**: {hospital['phone']}")
                st.write(f"**거리**: {hospital['distance']}")
                if hospital['url']:
                    st.write(f"[상세 정보 보기]({hospital['url']})")
```

#### 3. **사이드바 설정**
```python
with st.sidebar:
    st.header("⚙️ 설정")
    
    # 검색 단계 선택
    stage = st.selectbox(
        "검색 방식",
        [1, 2, 3],
        index=2,
        format_func=lambda x: {
            1: "1단계 - Threshold",
            2: "2단계 - MMR",
            3: "3단계 - Ensemble"
        }[x]
    )
    
    # 검색 문서 수
    k = st.slider("검색 문서 수", 3, 10, 5)
    
    # Threshold 값
    threshold = st.slider("유사도 임계값", 0.0, 1.0, 0.6, 0.1)
    
    # 대화 기록
    if st.button("🗑️ 대화 기록 삭제"):
        st.session_state.messages = []
        st.rerun()
```

### **UI 특징**
- 💬 **실시간 채팅 인터페이스**: 카카오톡과 유사한 직관적인 대화형 UI
- ⚙️ **사용자 맞춤 설정**: 검색 방식, 문서 수, 임계값 조절 가능
- 💾 **대화 기록 저장**: 이전 대화 내용 확인 및 관리

---



### **추천 시스템 흐름**
```
1. 사용자 위치 입력
   ├─ 자동 감지 (IP 기반)
   └─ 수동 입력 (주소/좌표)
   ↓
2. Kakao Maps API 호출
   ├─ 키워드: "동물병원"
   ├─ 반경: 5km
   └─ 정렬: 거리순
   ↓
3. 결과 필터링 및 정렬
   ├─ 영업 중인 병원 우선
   ├─ 평점 정보 포함 (있는 경우)
   └─ 거리 표시 (km/m)
   ↓
4. 지도 시각화
   ├─ 사용자 위치 (빨간 마커)
   ├─ 병원 위치 (파란 마커)
   └─ 클릭 시 상세 정보 팝업
   ↓
5. 리스트 출력
   └─ 병원별 상세 정보 카드
```

---

## 🔧 설치 및 실행

### **1. 환경 설정**

#### **필수 요구사항**
- Python 3.9 이상
- OpenAI API Key
- Kakao REST API Key (병원 추천 기능용)

#### **패키지 설치**
```bash
# 가상환경 생성 (선택)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt
```

#### **환경 변수 설정** (`.env` 파일)
```env
OPENAI_API_KEY=your_openai_api_key_here
KAKAO_REST_API_KEY=your_kakao_api_key_here
LANGSMITH_API_KEY=your_langsmith_key_here  # (선택) LangSmith 모니터링용
```

### **2. 데이터 준비**

#### **데이터 전처리**
```bash
# 원천 데이터에서 청킹된 문서 생성
python data_preprocessing.py
# → chunked_docs.pkl 파일 생성
```

#### **벡터스토어 구축**
```bash
# ChromaDB에 임베딩 저장
python vectorstore.py
# → ./ChromaDB/pet_health_qa_system 생성
```

### **3. 시스템 테스트**

#### **Retriever 테스트**
```bash
# 검색 시스템 성능 테스트
python test_retriever.py
```

#### **Prompt 테스트**
```bash
# 질의응답 체인 테스트
python prompt.py
```

### **4. 챗봇 실행**

```bash
# Streamlit 앱 실행
streamlit run app.py
```

브라우저에서 `http://localhost:8501` 접속

---

## 📈 성능 및 최적화

### **검색 성능**

| 검색 방법 | 정확도 | 다양성 | 속도 | 권장 사용 |
|----------|--------|--------|------|----------|
| **1단계 - Threshold** | ★★★☆☆ | ★★☆☆☆ | ★★★★★ | 빠른 응답 필요 시 |
| **2단계 - MMR** | ★★★★☆ | ★★★★★ | ★★★★☆ | 다양한 관점 필요 시 |
| **3단계 - Ensemble** | ★★★★★ | ★★★★☆ | ★★★☆☆ | 최고 품질 답변 필요 시 |

### **최적화 기법**

#### **1. 문서 캐싱**
```python
class DocumentCache:
    """반복 검색 시 성능 향상 (최대 1시간 캐싱)"""
    def get_all_docs(self, vectorstore, k=1000, max_age=3600):
        if cache is expired:
            self.all_docs_cache = vectorstore.similarity_search("", k=k)
        return self.all_docs_cache
```

#### **2. 배치 임베딩**
```python
# 대용량 데이터 처리 시 배치 단위로 임베딩
BATCH_SIZE = 100
for i in range(0, len(docs), BATCH_SIZE):
    batch = docs[i:i + BATCH_SIZE]
    vectorstore.add_documents(batch)
    time.sleep(1)  # API Rate Limit 방지
```

#### **3. 적응형 Threshold**
```python
def adaptive_threshold_retriever(query, k=10, percentile=0.7):
    """
    검색 결과의 상위 N%만 선택하는 동적 threshold
    - 고정 threshold의 한계 극복
    """
    results = vectorstore.similarity_search_with_score(query, k=k*3)
    dynamic_threshold = calculate_percentile_threshold(results, percentile)
    return filter_by_threshold(results, dynamic_threshold)
```

### **할루시네이션 방지 메커니즘**

1. **문맥 기반 필터링**: 검색된 문서만을 컨텍스트로 제공
2. **출처 강제**: 답변에 사용한 모든 문서의 출처 명시 요구
3. **Threshold 적용**: 유사도가 낮은 문서 제외 (기본 0.6)
4. **프롬프트 가드레일**: "문맥에 없는 정보는 절대 사용하지 마세요" 명시

---

## 🎓 기술 스택

### 🧠 AI / ML
![LangChain](https://img.shields.io/badge/LangChain-000000?style=flat&logo=chainlink&logoColor=white)
![LangGraph](https://img.shields.io/badge/LangGraph-5A00FF?style=flat&logo=graphql&logoColor=white)
![GPT-4o-mini](https://img.shields.io/badge/GPT--4o--mini-412991?style=flat&logo=openai&logoColor=white)
![OpenAI Embeddings](https://img.shields.io/badge/Embeddings-text--embedding--3--small-00A67E?style=flat&logo=openai&logoColor=white)

---

### 🗂️ Vector Database
![ChromaDB](https://img.shields.io/badge/ChromaDB-FF5A1F?style=flat&logo=databricks&logoColor=white)
![HNSW](https://img.shields.io/badge/HNSW-005BBB?style=flat&logo=elastic&logoColor=white)

---

### 🔍 검색 알고리즘
![Similarity Search](https://img.shields.io/badge/Similarity_Search-333333?style=flat&logo=google&logoColor=white)
![MMR](https://img.shields.io/badge/MMR-6A5ACD?style=flat&logo=replit&logoColor=white)
![BM25](https://img.shields.io/badge/BM25-0B72B9?style=flat&logo=apache%20solr&logoColor=white)
![Ensemble](https://img.shields.io/badge/Ensemble-444444?style=flat&logo=codecov&logoColor=white)

---

### 🌐 Frontend
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=flat&logo=streamlit&logoColor=white)

---

### 🛠️ Development Tools
![Python](https://img.shields.io/badge/Python-3.12-blue?style=flat&logo=python&logoColor=white)
![Python-dotenv](https://img.shields.io/badge/python--dotenv-3776AB?style=flat&logo=python&logoColor=white)


---

## 🚀 향후 개선 방향

### **1. 기능 확장**
- [ ] **다중 언어 지원**: 영어, 일본어 등 추가
- [ ] **이미지 분석**: 증상 사진 업로드 및 분석
- [ ] **음성 인터페이스**: STT/TTS 통합
- [ ] **예방접종 알림**: 반려견 프로필 기반 스케줄 관리

### **2. 성능 개선**
- [ ] **모델 파인튜닝**: 수의학 도메인 특화 모델 학습
- [ ] **캐싱 고도화**: Redis 기반 분산 캐싱
- [ ] **비동기 처리**: 병렬 검색으로 응답 속도 향상
- [ ] **Reranking**: Cross-Encoder 추가로 검색 정확도 향상

### **3. 데이터 확장**
- [ ] **최신 논문 추가**: arXiv, PubMed 자동 크롤링
- [ ] **사용자 피드백 학습**: RLHF 적용
- [ ] **증상-질병 지식 그래프**: Neo4j 기반 관계 모델링
- [ ] **계절별 질병 데이터**: 시즌별 맞춤 정보

### **4. UX 개선**
- [ ] **모바일 앱**: Flutter/React Native 개발
- [ ] **챗봇 개성화**: 다양한 캐릭터 선택 옵션
- [ ] **병원 예약 연동**: 직접 예약 기능
- [ ] **커뮤니티 기능**: 보호자 간 경험 공유

### **5. 안전성 강화**
- [ ] **의료면책 고지**: 명확한 책임 범위 표시
- [ ] **응급 상황 감지**: 위험 키워드 자동 감지 및 119 안내
- [ ] **개인정보 보호**: 대화 기록 암호화 저장
- [ ] **수의사 검증**: 전문가 리뷰 시스템 도입

---

## 📝 프로젝트 한줄 회고

| 이름 | 회고 |
|------|------|
| **박찬** | "RAG 시스템 구축의 A to Z를 경험하며 LLM 활용의 실무 감각을 얻었습니다." |
| **김나현** | "데이터 전처리의 중요성을 깨달았고, 청킹 전략이 검색 성능에 미치는 영향을 체감했습니다." |
| **이도경** | "3단계 하이브리드 검색을 구현하며 각 알고리즘의 장단점을 명확히 이해할 수 있었습니다." |
| **안채연** | "사용자 관점에서 직관적인 UI를 설계하는 과정이 AI 서비스의 핵심임을 느꼈습니다." |
| **이경현** | "외부 API 연동을 통해 단순 챗봇을 넘어 실용적인 서비스로 확장하는 즐거움을 배웠습니다." |

---

## 📄 라이선스

이 프로젝트는 교육 목적으로 제작되었으며, 실제 의료 조언을 대체할 수 없습니다.  
반려동물의 건강에 문제가 있다면 반드시 수의사와 상담하세요.

---

