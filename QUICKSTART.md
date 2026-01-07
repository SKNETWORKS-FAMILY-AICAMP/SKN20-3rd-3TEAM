# Docker + FastAPI 실행 가이드

## 🚀 빠른 시작 (3단계)

### 1단계: 환경 변수 설정
```powershell
# .env 파일 생성
copy .env.example .env

# .env 파일 편집 (메모장으로 열기)
notepad .env
```

**.env 파일 내용:**
```env
OPENAI_API_KEY=sk-your-actual-openai-key-here
```

### 2단계: Docker 실행
```powershell
# SKN20-3rd-3TEAM 폴더에서
docker-compose up --build
```

### 3단계: 접속
- **Streamlit UI**: http://localhost:8501
- **API 문서**: http://localhost:8000/docs

---

## ⚙️ 명령어 모음

```powershell
# 시작
docker-compose up

# 백그라운드 실행
docker-compose up -d

# 재빌드 후 실행
docker-compose up --build

# 중지
docker-compose stop

# 중지 + 컨테이너 삭제
docker-compose down

# 로그 확인
docker-compose logs -f
```

---

## 📋 체크리스트

- [ ] Docker Desktop 설치됨
- [ ] .env 파일에 OPENAI_API_KEY 입력됨
- [ ] data/ChromaDB_bge_m3 폴더 존재함 (벡터DB)
- [ ] docker-compose up 실행됨
- [ ] http://localhost:8501 접속 가능

---

## ❌ 오류 해결

**포트 충돌 시:**
```yaml
# docker-compose.yml에서 포트 변경
ports:
  - "8080:8000"  # backend
  - "8502:8501"  # frontend
```

**API 키 오류 시:**
- .env 파일 확인
- docker-compose down 후 재시작

**벡터DB 없음 오류 시:**
```powershell
# 먼저 벡터DB 생성
cd src
python vectorstore_bge_m3.py
```
