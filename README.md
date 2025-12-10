# 반려견 건강 상담 AI 챗봇

반려견의 질병 및 증상에 대한 정보를 제공하는 RAG 기반 AI 어시스턴트

## 📁 프로젝트 구조

```
SKN20-3rd-3TEAM/
├── 1.데이터/                      # 학습 및 검증 데이터
│   ├── Training/
│   │   └── 02.라벨링데이터/
│   │       ├── TL_질의응답데이터_내과/
│   │       ├── TL_질의응답데이터_안과/
│   │       ├── TL_질의응답데이터_외과/
│   │       ├── TL_질의응답데이터_치과/
│   │       └── TL_질의응답데이터_피부과/
│   └── Validation/
│
├── src/                           # 모듈화된 소스코드
│   ├── data/                      # 데이터 전처리
│   │   ├── __init__.py
│   │   └── preprocessor.py        # DataPreprocessor 클래스
│   │
│   ├── vectorstore/               # 벡터 DB 관리
│   │   ├── __init__.py
│   │   └── manager.py             # VectorStoreManager 클래스
│   │
│   ├── retrieval/                 # 문서 검색
│   │   ├── __init__.py
│   │   └── hybrid_retriever.py    # HybridRetriever (Chroma + BM25)
│   │
│   ├── generation/                # 응답 생성
│   │   ├── __init__.py
│   │   └── llm_chain.py           # LLMChain (프롬프트 + GPT-4)
│   │
│   ├── utils/                     # 유틸리티
│   │   ├── __init__.py
│   │   └── helpers.py             # 헬퍼 함수들
│   │
│   └── pipeline.py                # RAG 파이프라인 통합
│
├── app.py                         # Streamlit 웹 인터페이스
├── requirements.txt               # 패키지 의존성
├── chroma_db/                     # 벡터 DB 저장소
└── chunked_docs.pkl               # 청크된 문서 캐시
```

## 🚀 빠른 시작

### 1. 환경 설정

```powershell
# 가상환경 생성 (선택사항)
python -m venv venv
.\venv\Scripts\Activate.ps1

# 패키지 설치
pip install -r requirements.txt
```

### 2. 환경 변수 설정

프로젝트 루트에 `.env` 파일 생성:

```
OPENAI_API_KEY=your_api_key_here
```

### 3. Streamlit 앱 실행

```powershell
streamlit run app.py
```

브라우저가 자동으로 열리며 `http://localhost:8501`에서 실행됩니다.

### 4. CLI 모드 실행 (선택사항)

```powershell
python -m src.pipeline
```

## 🛠️ 주요 기능

### 1. 데이터 전처리 (`src/data/preprocessor.py`)
- 의료 데이터 및 QA 데이터 로드
- RecursiveCharacterTextSplitter로 청킹
- 메타데이터 관리 (출처, 생애주기, 과, 질병 등)

### 2. 벡터 DB 관리 (`src/vectorstore/manager.py`)
- Chroma DB 생성 및 로드
- 배치 처리 (500개 단위)
- 에러 핸들링 및 재시도 로직

### 3. 하이브리드 검색 (`src/retrieval/hybrid_retriever.py`)
- MMR (50%) + BM25 (50%) 앙상블
- 가중치 기반 문서 스코어링
- Top-K 문서 반환

### 4. LLM 응답 생성 (`src/generation/llm_chain.py`)
- GPT-4o-mini 기반 응답 생성
- 쿼리 재작성 (검색 최적화)
- 할루시네이션 방지 프롬프트

### 5. 통합 파이프라인 (`src/pipeline.py`)
- 전체 워크플로우 오케스트레이션
- 캐시 관리
- 대화형 쿼리 인터페이스

### 6. Streamlit 웹 앱 (`app.py`)
- 직관적인 채팅 UI
- 실시간 응답 생성
- 출처 문서 표시
- 대화 기록 관리

## 📊 데이터 구조

### QA 데이터 메타데이터
```python
{
    'source_type': 'qa_data',
    'life_stage': '성견',
    'department': '내과',
    'disease': '구토'
}
```

### 의료 데이터 메타데이터
```python
{
    'source_type': 'medical_data',
    'book_title': '수의학 개론',
    'author': '홍길동',
    'publisher': '출판사명'
}
```

## 🔧 커스터마이징

### 검색 파라미터 조정

`src/pipeline.py`의 `RAGPipeline.__init__()`:

```python
chroma_retriever = self.vectorstore_manager.get_retriever(
    k=5, 
    search_type="mmr"  # MMR 검색 사용
)
self.hybrid_retriever = HybridRetriever(
    documents=chunked_docs,
    chroma_retriever=chroma_retriever,
    chroma_weight=0.5,  # MMR 가중치
    bm25_weight=0.5,    # BM25 가중치
    k=5                 # 반환 문서 수
)
```

### LLM 모델 변경

`src/generation/llm_chain.py`의 `LLMChain.__init__()`:

```python
self.llm = ChatOpenAI(
    model="gpt-4o-mini",  # 모델명
    temperature=0         # 생성 온도
)
```

### 청킹 전략 수정

`src/data/preprocessor.py`의 `DataPreprocessor.chunk_documents()`:

```python
splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,      # 청크 크기
    chunk_overlap=100,   # 오버랩 크기
    separators=["\n\n", "\n", ".", " "]
)
```

## 🧪 테스트

### 파이프라인 테스트

```powershell
python -m src.pipeline
```

### 개별 모듈 테스트

```powershell
# 데이터 전처리
python -c "from src.data.preprocessor import DataPreprocessor; dp = DataPreprocessor(); docs = dp.process_all_data(); print(f'Total docs: {len(docs)}')"

# 벡터스토어
python -c "from src.vectorstore.manager import VectorStoreManager; vm = VectorStoreManager(); vm.load_vectorstore(); print('VectorStore loaded')"

# 하이브리드 검색
python -c "from src.retrieval.hybrid_retriever import HybridRetriever; print('HybridRetriever imported')"
```

## 🐛 트러블슈팅

### 1. Import 오류
```
ModuleNotFoundError: No module named 'src'
```
**해결책**: 프로젝트 루트에서 실행하세요.

```powershell
cd c:\LDG_CODES\SKN20\SKN20-3rd-3TEAM
python -m src.pipeline
```

### 2. OpenAI API 오류
```
ValueError: .env 파일에 OPENAI_API_KEY를 설정하세요
```
**해결책**: `.env` 파일에 API 키 추가

### 3. 데이터 경로 오류
```
FileNotFoundError: [Errno 2] No such file or directory
```
**해결책**: `1.데이터/` 폴더가 프로젝트 루트에 있는지 확인

### 4. Chroma DB 오류
```
chromadb.errors.InvalidCollectionException
```
**해결책**: `chroma_db/` 폴더 삭제 후 재생성

```powershell
Remove-Item -Recurse -Force .\chroma_db
python -m src.pipeline
```

## 📝 라이센스

이 프로젝트는 교육 목적으로 제작되었습니다.

## 👥 기여자

- SKN20-3rd-3TEAM

## 📞 문의

프로젝트 관련 문의사항은 이슈를 등록해주세요.
