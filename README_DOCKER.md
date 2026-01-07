# 🐕 반려견 질병 상담 챗봇 - Docker + FastAPI 버전

## 📌 개선 사항

### 기존 구조 → 개선된 구조

**Before:**
```
Streamlit (Frontend + Backend 통합)
    ↓
LangChain RAG Pipeline
    ↓
ChromaDB + OpenAI API
```

**After:**
```
Frontend (Streamlit)  ← HTTP →  Backend (FastAPI)
                                    ↓
                            LangChain RAG Pipeline
                                    ↓
                            ChromaDB + OpenAI API
```

### 주요 개선 사항

✅ **아키텍처 분리**: Frontend/Backend 완전 분리  
✅ **RESTful API**: FastAPI 기반 표준 API 제공  
✅ **Docker 컨테이너화**: 일관된 배포 환경  
✅ **자동 API 문서**: Swagger UI 자동 생성  
✅ **확장성**: 마이크로서비스 아키텍처 기반  
✅ **성능 향상**: 비동기 처리 지원  

---

## 🚀 빠른 시작

### 1. 사전 준비

**필수 도구:**
- Docker Desktop (Windows)
- Docker Compose
- `.env` 파일 설정

**환경 변수 설정:**
```powershell
# .env.example을 복사하여 .env 생성
cp .env.example .env

# .env 파일 편집하여 API Key 입력
# OPENAI_API_KEY=your_actual_api_key_here
```

### 2. Docker로 실행

```powershell
# 프로젝트 루트 디렉토리에서 실행
cd c:\LDG_CODES\SKN20\SKN20-3rd-3TEAM

# Docker 컨테이너 빌드 및 실행
docker-compose up --build

# 백그라운드 실행 (선택)
docker-compose up -d
```

### 3. 서비스 접속

- **Frontend (Streamlit)**: http://localhost:8501
- **Backend API**: http://localhost:8000
- **API 문서 (Swagger)**: http://localhost:8000/docs
- **API 문서 (ReDoc)**: http://localhost:8000/redoc

### 4. 종료

```powershell
# 컨테이너 정지 및 제거
docker-compose down

# 볼륨까지 완전 삭제
docker-compose down -v
```

---

## 📂 프로젝트 구조

```
SKN20-3rd-3TEAM/
├── backend/                    # FastAPI 백엔드
│   ├── app/
│   │   ├── api/
│   │   │   └── v1/
│   │   │       └── endpoints.py    # API 엔드포인트
│   │   ├── core/
│   │   │   └── config.py           # 설정
│   │   ├── models/
│   │   │   └── schemas.py          # Pydantic 모델
│   │   ├── services/
│   │   │   └── rag_service.py      # RAG 비즈니스 로직
│   │   └── main.py                 # FastAPI 앱
│   ├── Dockerfile
│   └── requirements.txt
│
├── frontend/                   # Streamlit 프론트엔드
│   ├── streamlit_app.py        # Streamlit UI (FastAPI 클라이언트)
│   ├── Dockerfile
│   └── requirements.txt
│
├── src/                        # 기존 소스 (공유)
│   ├── ensemble.py
│   ├── preprocessing.py
│   └── ...
│
├── data/                       # 벡터 DB 데이터
│   └── ChromaDB_bge_m3/
│
├── docker-compose.yml          # Docker Compose 설정
├── .env.example                # 환경변수 템플릿
└── README_DOCKER.md            # 이 문서
```

---

## 🔌 API 엔드포인트

### 1. 채팅 질의응답
```http
POST /api/v1/chat
Content-Type: application/json

{
  "question": "강아지가 기침을 해요",
  "search_type": "ensemble",
  "k": 5,
  "use_rewrite": false
}
```

**Response:**
```json
{
  "answer": "강아지 기침은 다양한 원인이...",
  "sources": [...],
  "search_type": "ensemble",
  "rewritten_query": null
}
```

### 2. 문서 검색
```http
POST /api/v1/search
Content-Type: application/json

{
  "query": "구토",
  "search_type": "similarity",
  "k": 10
}
```

### 3. 헬스 체크
```http
GET /api/v1/health
```

**Response:**
```json
{
  "status": "healthy",
  "chromadb_status": "ok",
  "model_loaded": true,
  "vectorstore_count": 30000
}
```

---

## 🛠️ 개발 모드

### Backend만 실행 (로컬)

```powershell
cd backend

# 가상환경 생성 및 활성화
python -m venv venv
.\venv\Scripts\activate

# 패키지 설치
pip install -r requirements.txt

# FastAPI 서버 실행 (Hot Reload)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend만 실행 (로컬)

```powershell
cd frontend

# 패키지 설치
pip install -r requirements.txt

# Streamlit 실행
streamlit run streamlit_app.py
```

---

## 🧪 API 테스트

### cURL 예제

```powershell
# 채팅 요청
curl -X POST "http://localhost:8000/api/v1/chat" `
  -H "Content-Type: application/json" `
  -d '{\"question\":\"강아지가 설사를 해요\",\"search_type\":\"ensemble\",\"k\":5}'

# 헬스 체크
curl http://localhost:8000/api/v1/health
```

### Python 예제

```python
import requests

# 채팅 요청
response = requests.post(
    "http://localhost:8000/api/v1/chat",
    json={
        "question": "강아지가 기침을 해요",
        "search_type": "ensemble",
        "k": 5,
        "use_rewrite": False
    }
)
print(response.json())
```

---

## 📊 모니터링

### 로그 확인

```powershell
# 실시간 로그 확인
docker-compose logs -f

# 특정 서비스만
docker-compose logs -f backend
docker-compose logs -f frontend
```

### 컨테이너 상태 확인

```powershell
# 실행 중인 컨테이너 목록
docker-compose ps

# 리소스 사용량
docker stats
```

---

## 🔧 트러블슈팅

### 문제 1: 포트 충돌
```powershell
# 포트 사용 확인
netstat -ano | findstr :8000
netstat -ano | findstr :8501

# docker-compose.yml에서 포트 변경
ports:
  - "8080:8000"  # 8000 대신 8080 사용
```

### 문제 2: 벡터스토어 로드 실패
```
원인: data/ChromaDB_bge_m3 폴더가 없거나 비어있음

해결:
1. src/vectorstore_bge_m3.py 먼저 실행하여 벡터DB 생성
2. data 폴더가 올바르게 마운트되었는지 확인
```

### 문제 3: OpenAI API 키 오류
```
원인: .env 파일에 API 키 미설정

해결:
1. .env 파일 생성 (cp .env.example .env)
2. OPENAI_API_KEY=sk-... 입력
3. docker-compose down 후 재시작
```

---

## 🚀 배포 (선택)

### AWS EC2 배포 예시

```bash
# EC2 인스턴스에서
sudo yum update -y
sudo yum install docker -y
sudo systemctl start docker

# Docker Compose 설치
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 프로젝트 클론
git clone <repository>
cd SKN20-3rd-3TEAM

# .env 설정
vim .env

# 실행
docker-compose up -d
```

---

## 📝 기존 코드와의 차이점

| 항목 | 기존 (Streamlit) | 개선 (FastAPI + Docker) |
|------|------------------|-------------------------|
| 아키텍처 | Monolithic | Microservices |
| 배포 | 수동 설치 | Docker 컨테이너 |
| API | 없음 | RESTful API |
| 문서화 | README | Swagger 자동 생성 |
| 확장성 | 제한적 | 수평 확장 가능 |
| 성능 | 동기 처리 | 비동기 처리 지원 |

---

## 💡 다음 단계

**추가 개선 가능 사항:**
1. Redis 캐싱 추가
2. Nginx Load Balancer
3. Prometheus + Grafana 모니터링
4. CI/CD 파이프라인 (GitHub Actions)
5. Kubernetes 배포

---

## 👥 팀원
- **박찬** (팀장)
- **김나현**
- **이도경**
- **안채연**
- **이경현**

---

## 📄 라이선스
이 프로젝트는 교육 목적으로 제작되었습니다.
