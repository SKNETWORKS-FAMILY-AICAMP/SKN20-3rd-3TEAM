# 강아지 증상 상담 챗봇 🐕

RAG 기반 강아지 증상 상담 및 동물병원 추천 챗봇

## 기능

- 강아지 증상 기반 질병 진단 및 상담
- LangChain + LangGraph를 활용한 RAG 파이프라인
- OpenAI GPT-4o-mini 모델 사용
- 지도 API 연동 (카카오/네이버/구글)
- 근처 동물병원 자동 검색 및 추천

## 설치 방법

### 1. 가상환경 생성
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 2. 패키지 설치
```bash
cd dog-symptom-chatbot
pip install -r requirements.txt
```

### 3. 환경변수 설정
```bash
cp .env.example .env
# .env 파일을 열어서 API 키 입력
```

## 사용 방법

### 1. 데이터 적재
JSON 파일들을 `data/raw_json/` 폴더에 넣고:
```bash
python -m app.ingest
```

### 2. 서버 실행
```bash
uvicorn app.main:app --reload --port 8000
```

### 3. API 테스트
```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "우리 강아지가 기침을 자주 해요",
    "location": "서울 강남구"
  }'
```

## API 문서

서버 실행 후 http://localhost:8000/docs 에서 확인

## 프로젝트 구조

```
dog-symptom-chatbot/
├── app/
│   ├── __init__.py
│   ├── config.py          # 설정 관리
│   ├── ingest.py          # 데이터 적재
│   ├── rag_chain.py       # RAG 체인
│   ├── graph.py           # LangGraph 정의
│   ├── maps_client.py     # 지도 API 클라이언트
│   └── main.py            # FastAPI 서버
├── data/
│   ├── raw_json/          # JSON 데이터 (여기에 파일 넣기)
│   └── vector_store/      # 벡터스토어 (자동 생성)
├── .env
├── .env.example
├── requirements.txt
└── README.md
```

## 라이센스

MIT License
