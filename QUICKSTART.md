# 🚀 빠른 시작 가이드 (Quick Start)

## 5분 안에 시작하기

### 1단계: 필수 패키지 설치 (1분)

```bash
pip install -r requirements.txt
```

### 2단계: API 키 설정 (2분)

`.env` 파일을 프로젝트 루트에 생성:

```bash
# .env 파일 내용
OPENAI_API_KEY=sk-your-key-here
TAVILY_API_KEY=tvly-your-key-here  # 선택사항
```

**API 키 획득:**
- **OpenAI**: https://platform.openai.com/api-keys
- **Tavily**: https://tavily.com/

### 3단계: 앱 실행 (1분)

```bash
streamlit run app.py
```

**자동으로 브라우저가 열립니다** → `http://localhost:8501`

### 4단계: 질문하기 (1분)

1. 텍스트 상자에 질문 입력
2. "📤 제출" 버튼 클릭
3. AI 답변 확인
4. 📚 "참고한 문서" 확인

---

## 📌 첫 질문 예시

```
🔍 입력: "강아지 피부 질환의 증상은 무엇인가요?"

💡 기대 결과:
   - AI가 질병 증상 설명
   - 참고 문서 3-5개 표시
   - 약 2-3초 내 응답
```

---

## ⚠️ 일반적인 오류 및 해결

| 오류 | 원인 | 해결 |
|------|------|------|
| `OPENAI_API_KEY not found` | API 키 미설정 | `.env` 파일에 API 키 추가 |
| `Chroma DB not found` | 벡터 DB 없음 | 기존 `chroma_db` 디렉토리 확인 |
| `Port 8501 already in use` | 포트 충돌 | `streamlit run app.py --server.port 8502` |
| `ModuleNotFoundError: streamlit` | 미설치 | `pip install streamlit` |
| `Connection timeout` | 네트워크 오류 | 인터넷 연결 확인 |

---

## 🎯 주요 기능 테스트

### 기본 기능 테스트 체크리스트

- [ ] **질문 입력 및 제출**: 텍스트 입력 후 버튼 클릭
- [ ] **답변 표시**: AI 답변 화면에 표시됨
- [ ] **출처 정보**: "참고한 문서" 섹션 확인
- [ ] **대화 이력**: 여러 질문 후 이력 표시됨
- [ ] **대화 초기화**: "대화 초기화" 버튼으로 초기화

### 고급 기능 테스트 체크리스트

- [ ] **디버그 정보**: 사이드바에서 활성화 후 정보 표시
- [ ] **통계**: "통계" 버튼으로 대화 통계 확인
- [ ] **예시 질문**: 예시 질문 클릭 시 자동 입력
- [ ] **웹 검색**: 내부 문서 없는 질문 후 웹 검색 여부 확인

---

## 💻 시스템 요구사항

### 최소 사양
- **OS**: Windows 10+, macOS 10.14+, Linux
- **Python**: 3.8+
- **RAM**: 4GB
- **스토리지**: 2GB (Chroma DB 포함)

### 권장 사양
- **Python**: 3.10+
- **RAM**: 8GB+
- **GPU**: NVIDIA (선택사항, 임베딩 가속)

---

## 🔗 다음 단계

### 기본 사용
1. ✅ 앱 실행 확인
2. 📝 여러 질문 테스트
3. 📊 결과 및 출처 확인

### 고급 사용
1. 🐛 디버그 정보 분석
2. ⚙️ LLM 모델 변경
3. 🔧 Top-K 값 조정

### 배포
1. 🌐 클라우드 배포 (Streamlit Cloud)
2. 🐳 Docker 컨테이너화
3. 📱 모바일 최적화

---

## 📞 빠른 도움말

**Q: 앱이 느림**
```bash
# 더 빠른 모델 사용
streamlit run app.py
# app.py의 llm_model을 "gpt-4o-mini"로 변경
```

**Q: 답변 품질이 낮음**
```bash
# 더 나은 모델 사용
# app.py의 llm_model을 "gpt-4o"로 변경
```

**Q: 웹 검색이 작동하지 않음**
```bash
# Tavily API 키 확인
# .env 파일에 TAVILY_API_KEY=... 추가
```

**Q: 다른 포트에서 실행**
```bash
streamlit run app.py --server.port 8502
```

---

## 📚 전체 가이드 읽기

더 자세한 내용은 [STREAMLIT_GUIDE.md](./STREAMLIT_GUIDE.md)를 참조하세요.

- 🎨 UI 상세 설명
- 🔧 고급 설정
- 🐛 디버그 정보 해석
- ⚙️ 성능 최적화
- 🚨 트러블슈팅

---

## ✨ 팁 및 트릭

### 생산성 향상
```bash
# 자동 새로고침 활성화
streamlit run app.py --logger.level=debug

# 빠른 개발 모드
streamlit run app.py --client.showErrorDetails=true
```

### 디버깅
```bash
# 로그 출력 활성화
streamlit run app.py --logger.level=info

# 디버그 정보 확인
# 앱의 "디버그 정보 표시" 체크박스 활성화
```

### 성능 모니터링
```bash
# 응답 시간 확인
# 각 답변 아래에 ⏱️ 응답 시간 표시
```

---

**성공적인 실행을 기원합니다! 🎉**

문제가 있으면 [STREAMLIT_GUIDE.md](./STREAMLIT_GUIDE.md)의 트러블슈팅 섹션을 참조하세요.

