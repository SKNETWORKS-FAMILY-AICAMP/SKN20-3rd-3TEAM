# 📍 GPS 위치 기반 병원 추천 기능 가이드

## 📌 개요

`streamlit-geolocation` 라이브러리를 사용하여 사용자의 GPS 좌표를 획득하고, 카카오 지도 API로 가장 가까운 동물병원 3곳을 추천합니다.

---

## 🔧 1. 패키지 설치

### 필수 패키지 설치

```powershell
pip install streamlit-geolocation
```

또는 `requirements_streamlit.txt`로 일괄 설치:

```powershell
pip install -r requirements_streamlit.txt
```

**`requirements_streamlit.txt` 내용**:
```txt
streamlit>=1.28.0
streamlit-geolocation>=0.0.5  # GPS 위치 요청용
plotly>=5.17.0
```

---

## 🗺️ 2. GPS 위치 요청 흐름

### 사용자 시나리오

```
1. 사용자: "강아지가 구토를 해요"
   ↓
2. Agent: [증상 분석] → [응급도: 높음]
   ↓
3. Streamlit: "🚨 병원 추천이 필요합니다. GPS 위치를 공유하거나 주소를 입력하세요."
   ↓
4. 사용자: [📍 GPS 위치 공유] 버튼 클릭
   ↓
5. 브라우저: "위치 정보 접근 권한 요청"
   ↓
6. 사용자: "허용" 클릭
   ↓
7. Streamlit: GPS 좌표 획득 (lat, lon)
   ↓
8. 카카오 API: 좌표 기준 5km 이내 동물병원 검색
   ↓
9. Streamlit: 병원 3곳 추천 (거리순)
```

---

## 💻 3. 코드 구현 설명

### 3.1. `src/utils/tools.py` - GPS 좌표 처리

**수정된 함수**:

```python
def search_nearby_hospitals(query: str = None, lat: float = None, lon: float = None) -> List[Dict]:
    """
    주소(query) 또는 위도/경도(lat, lon)를 기반으로 주변 동물병원 검색
    """
    x_coord, y_coord = None, None
    
    # GPS 좌표가 있으면 직접 사용
    if lat is not None and lon is not None:
        x_coord, y_coord = lon, lat  # 카카오는 x=경도, y=위도
    
    # 주소 문자열이 있으면 Geocoding
    elif query:
        # 기존 카카오 주소 검색 API 호출 로직
        ...
    
    # 좌표 기준으로 동물병원 검색
    keyword_params = {
        "query": "동물병원",
        "x": x_coord,
        "y": y_coord,
        "radius": 5000,  # 5km 이내
        "sort": "distance"
    }
    ...
```

### 3.2. `app.py` - Streamlit GPS 요청 UI

**추가된 UI 컴포넌트**:

```python
from streamlit_geolocation import streamlit_geolocation

# 세션 상태에 GPS 좌표 저장
if "user_gps_location" not in st.session_state:
    st.session_state.user_gps_location = None

# GPS 위치 요청 버튼
if st.button("📍 GPS 위치 공유", type="primary"):
    location_data = streamlit_geolocation()
    
    if location_data and location_data.get("latitude"):
        st.session_state.user_gps_location = {
            "lat": location_data["latitude"],
            "lon": location_data["longitude"]
        }
        st.success("✅ GPS 위치 획득 완료")
```

**병원 검색 시 GPS 우선 사용**:

```python
if st.session_state.user_gps_location:
    gps = st.session_state.user_gps_location
    hospital_result = hospital_recommend_tool.invoke(
        lat=gps["lat"], 
        lon=gps["lon"]
    )
else:
    # 텍스트 주소 사용
    hospital_result = hospital_recommend_tool.invoke(query=user_input)
```

---

## 🚀 4. 실행 방법

### 1단계: 패키지 설치

```powershell
pip install -r requirements_streamlit.txt
```

### 2단계: 환경 변수 설정

`.env` 파일에 카카오 API 키 추가:

```env
KAKAO_REST_API_KEY=your_kakao_api_key_here
```

### 3단계: Streamlit 실행

```powershell
streamlit run app.py
```

### 4단계: 브라우저에서 테스트

1. 증상 입력: "강아지가 구토를 해요"
2. **응급도 높음** → 병원 추천 화면 활성화
3. **[📍 GPS 위치 공유]** 버튼 클릭
4. 브라우저 권한 요청 → **"허용"** 클릭
5. 자동으로 주변 병원 3곳 추천

---

## 🔒 5. 브라우저 권한 설정

### Chrome

1. 주소창 왼쪽 자물쇠 아이콘 클릭
2. **사이트 설정** → **위치**
3. **허용** 선택

### Firefox

1. 주소창 왼쪽 자물쇠 아이콘 클릭
2. **권한** → **위치 접근**
3. **허용** 선택

### Edge

1. 주소창 오른쪽 **...** 클릭
2. **사이트 권한** → **위치**
3. **허용** 선택

---

## 🐛 6. 문제 해결

### Q1: "GPS 위치를 가져올 수 없습니다" 오류

**원인**:
- 브라우저 위치 권한 거부
- HTTPS 연결 필요 (일부 브라우저)
- 모바일 기기에서 GPS 비활성화

**해결 방법**:

1. **브라우저 권한 확인**:
   - Chrome: `chrome://settings/content/location`
   - Firefox: `about:preferences#privacy`

2. **HTTPS 사용** (로컬 테스트 시):
   ```powershell
   streamlit run app.py --server.enableXsrfProtection false
   ```

3. **대체 방법**: 수동 주소 입력 사용

### Q2: GPS 좌표는 얻었는데 병원 검색 실패

**원인**:
- 카카오 API 키 미설정
- API 할당량 초과
- 좌표가 한국 외 지역

**해결 방법**:

1. API 키 확인:
   ```powershell
   echo $env:KAKAO_REST_API_KEY
   ```

2. 좌표 범위 확인:
   - 한국 위도: 33°~38°
   - 한국 경도: 124°~132°

### Q3: 버튼을 눌러도 반응이 없음

**원인**:
- `streamlit-geolocation` 패키지 미설치
- 브라우저 JavaScript 비활성화

**해결 방법**:

1. 패키지 재설치:
   ```powershell
   pip uninstall streamlit-geolocation
   pip install streamlit-geolocation
   ```

2. 브라우저 JavaScript 활성화 확인

---

## 📊 7. GPS vs 주소 입력 비교

| 구분 | GPS 위치 공유 | 주소 입력 |
|------|-------------|----------|
| **정확도** | ⭐⭐⭐⭐⭐ 매우 높음 | ⭐⭐⭐ 중간 |
| **속도** | ⚡ 1-2초 | ⏱️ 5-10초 (Geocoding) |
| **사용성** | 버튼 1번 클릭 | 주소 타이핑 필요 |
| **권한** | 브라우저 위치 권한 필요 | 불필요 |
| **오류율** | 낮음 | 주소 오타 가능성 |
| **적용 범위** | 현재 위치만 | 모든 지역 가능 |

**권장 사항**: GPS 우선 사용, 실패 시 주소 입력 대체

---

## 🧪 8. 테스트 시나리오

### 시나리오 1: GPS 성공

```
1. 증상 입력: "강아지가 발작을 해요"
2. 응급도: 높음 → 병원 추천 화면
3. [📍 GPS 위치 공유] 클릭
4. 브라우저 권한 허용
5. ✅ GPS (37.1234, 127.5678) 획득
6. 병원 3곳 자동 추천
```

### 시나리오 2: GPS 실패 → 주소 입력

```
1. 증상 입력: "고양이가 구토를 해요"
2. 응급도: 높음 → 병원 추천 화면
3. [📍 GPS 위치 공유] 클릭
4. ❌ GPS 위치 가져오기 실패
5. 채팅창에 "서울시 강남구 역삼동" 입력
6. Geocoding → 좌표 변환 → 병원 추천
```

---

## 📈 9. 성능 최적화

### 캐싱 활용

```python
from functools import lru_cache

@lru_cache(maxsize=100)
def search_nearby_hospitals_cached(lat, lon):
    return search_nearby_hospitals(lat=lat, lon=lon)
```

### GPS 좌표 재사용

- 세션 상태에 저장된 GPS 좌표는 병원 추천 완료 후 초기화
- 같은 위치에서 재검색 시 재사용 가능

---

## 🌐 10. 배포 시 고려사항

### Streamlit Cloud 배포

- **HTTPS 자동 활성화**: GPS 위치 요청 정상 작동
- **환경 변수 설정**: Secrets 메뉴에서 `KAKAO_REST_API_KEY` 추가

### Docker 배포

```dockerfile
# Dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt requirements_streamlit.txt ./
RUN pip install -r requirements.txt -r requirements_streamlit.txt

COPY . .

# HTTPS 설정 (선택)
EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0"]
```

**실행**:
```bash
docker build -t pet-health-chatbot .
docker run -p 8501:8501 -e KAKAO_REST_API_KEY=your_key pet-health-chatbot
```

---

**Made with 📍 for Pet Health AI**
