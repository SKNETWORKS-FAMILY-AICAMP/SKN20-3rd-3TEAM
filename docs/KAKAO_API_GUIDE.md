# 🗺️ 카카오 지도 API 연동 가이드

## 📌 개요

반려동물 건강 상담 챗봇에 **카카오 지도 API**를 연동하여 사용자 위치 기반으로 가장 가까운 동물병원 3곳을 자동으로 추천합니다.

---

## 🔑 1. 카카오 REST API 키 발급

### 1단계: 카카오 개발자 계정 생성

1. [카카오 개발자 사이트](https://developers.kakao.com/) 접속
2. **로그인** 또는 **회원가입**
3. 우측 상단 **내 애플리케이션** 클릭

### 2단계: 애플리케이션 추가

1. **애플리케이션 추가하기** 버튼 클릭
2. 앱 이름 입력: `반려동물건강챗봇` (자유롭게)
3. 사업자명 입력: 개인 또는 회사명
4. **저장** 클릭

### 3단계: REST API 키 확인

1. 생성된 앱 클릭
2. **앱 키** 탭에서 **REST API 키** 복사
   ```
   예: 1234567890abcdef1234567890abcdef
   ```

---

## 🔧 2. 환경 변수 설정

### Windows PowerShell

#### 임시 설정 (현재 세션만)

```powershell
$env:KAKAO_REST_API_KEY="1234567890abcdef1234567890abcdef"
```

#### 영구 설정 (시스템 환경 변수)

```powershell
[System.Environment]::SetEnvironmentVariable("KAKAO_REST_API_KEY", "1234567890abcdef1234567890abcdef", "User")
```

### `.env` 파일 사용 (권장)

프로젝트 루트 디렉토리에 `.env` 파일 생성:

```bash
# .env
OPENAI_API_KEY=sk-proj-...
ANTHROPIC_API_KEY=sk-ant-...
KAKAO_REST_API_KEY=1234567890abcdef1234567890abcdef
```

`.env` 파일 로드:

```python
from dotenv import load_dotenv
load_dotenv()
```

---

## 🧪 3. API 테스트

### 주소 → 좌표 변환 (Geocoding) 테스트

```python
import os
import requests

KAKAO_REST_API_KEY = os.getenv("KAKAO_REST_API_KEY")
HEADERS = {"Authorization": f"KakaoAK {KAKAO_REST_API_KEY}"}

# 주소를 좌표로 변환
geocode_url = "https://dapi.kakao.com/v2/local/search/address.json"
params = {"query": "서울시 강남구 역삼동"}

response = requests.get(geocode_url, headers=HEADERS, params=params)
result = response.json()

if result['documents']:
    x = result['documents'][0]['x']  # 경도
    y = result['documents'][0]['y']  # 위도
    print(f"좌표: ({x}, {y})")
else:
    print("주소를 찾을 수 없습니다.")
```

### 동물병원 검색 테스트

```python
# 좌표 기준 주변 동물병원 검색
keyword_url = "https://dapi.kakao.com/v2/local/search/keyword.json"
keyword_params = {
    "query": "동물병원",
    "category_group_code": "HP8",  # 병원 카테고리
    "x": x,  # 위에서 얻은 경도
    "y": y,  # 위에서 얻은 위도
    "radius": 5000,  # 5km 이내
    "sort": "distance",  # 거리순 정렬
    "size": 3  # 최대 3개
}

response = requests.get(keyword_url, headers=HEADERS, params=keyword_params)
hospital_result = response.json()

for i, hosp in enumerate(hospital_result['documents'], 1):
    print(f"{i}. {hosp['place_name']}")
    print(f"   주소: {hosp['road_address_name']}")
    print(f"   거리: {float(hosp['distance'])/1000:.2f}km")
    print(f"   전화: {hosp.get('phone', '정보 없음')}\n")
```

---

## 📂 4. 프로젝트 파일 구조

```
SKN20-3rd-3TEAM/
├── .env                          # 환경 변수 (KAKAO_REST_API_KEY 포함)
├── src/
│   ├── utils/
│   │   └── tools.py              # hospital_recommend_tool 구현
│   └── agent/
│       └── workflow.py           # LangGraph Agent에서 Tool 호출
├── app.py                        # Streamlit UI (병원 추천 통합)
└── docs/
    └── KAKAO_API_GUIDE.md        # 이 가이드
```

---

## 🚀 5. 실제 사용 예시

### Streamlit 앱에서 병원 추천

```python
# app.py 내부
from src.utils.tools import hospital_recommend_tool

location = "서울시 강남구 역삼동"
result = hospital_recommend_tool.invoke(location)

print(result)
```

**출력 예시**:

```
📍 사용자 위치 기준 가장 가까운 동물병원 정보입니다:

1. **24시 응급 동물병원**
   - 거리: 약 1.23 km
   - 주소: 서울 강남구 역삼동 123-45
   - 전화번호: 02-1234-5678

2. **스마일 동물 메디컬 센터**
   - 거리: 약 2.56 km
   - 주소: 서울 강남구 삼성동 678-90
   - 전화번호: 02-2345-6789

3. **펫케어 동물병원**
   - 거리: 약 3.14 km
   - 주소: 서울 강남구 논현동 456-78
   - 전화번호: 02-3456-7890
```

---

## 🛠️ 6. 문제 해결 (Troubleshooting)

### Q1: "API 키가 설정되지 않았습니다" 오류

**해결 방법**:

1. 환경 변수 확인:
   ```powershell
   echo $env:KAKAO_REST_API_KEY
   ```
2. `.env` 파일이 있다면:
   ```python
   from dotenv import load_dotenv
   load_dotenv()
   import os
   print(os.getenv("KAKAO_REST_API_KEY"))
   ```
3. Python에서 직접 설정 (테스트용):
   ```python
   import os
   os.environ["KAKAO_REST_API_KEY"] = "your_key_here"
   ```

### Q2: "주소 변환에 실패했습니다" 오류

**원인**:

- 주소가 너무 모호함
- 카카오가 인식하지 못하는 주소 형식

**해결 방법**:

- 더 구체적인 주소 입력: `"서울시 강남구 역삼동"` → `"서울시 강남구 역삼동 123-45"`
- 도로명 주소 사용: `"서울시 강남구 테헤란로 123"`

### Q3: "병원 검색에 실패했습니다" 오류

**원인**:

- API 할당량 초과
- 네트워크 연결 문제
- 잘못된 좌표

**해결 방법**:

1. API 할당량 확인: [카카오 개발자 사이트](https://developers.kakao.com/) → 내 애플리케이션 → 통계
2. 네트워크 확인:
   ```python
   import requests
   response = requests.get("https://dapi.kakao.com")
   print(response.status_code)  # 200이면 정상
   ```

### Q4: 검색 결과가 3개 미만

**원인**:

- 해당 지역에 동물병원이 적음
- 검색 반경(5km)이 좁음

**해결 방법**:

`src/utils/tools.py`에서 `radius` 값 증가:

```python
keyword_params = {
    "query": "동물병원",
    "category_group_code": "HP8",
    "x": x_coord,
    "y": y_coord,
    "radius": 10000,  # 5km → 10km로 변경
    "sort": "distance",
    "size": 3
}
```

---

## 🔒 7. 보안 주의사항

### API 키 노출 방지

1. **절대** GitHub에 업로드하지 마세요
   ```bash
   # .gitignore에 추가
   .env
   ```

2. `.env` 파일 예제 제공:
   ```bash
   # .env.example
   KAKAO_REST_API_KEY=your_key_here
   ```

3. Streamlit Cloud 배포 시:
   - Settings → Secrets에서 환경 변수 입력
   ```toml
   KAKAO_REST_API_KEY = "your_key_here"
   ```

---

## 📊 8. API 사용량 관리

### 카카오 로컬 API 할당량

- **무료 플랜**: 일 30만 건
- **초과 시**: API 차단 (24시간 후 재활성화)

### 사용량 확인

[카카오 개발자 사이트](https://developers.kakao.com/) → 내 애플리케이션 → 통계

### 캐싱으로 절약

```python
from functools import lru_cache

@lru_cache(maxsize=100)
def search_nearby_hospitals_cached(location_query: str):
    return search_nearby_hospitals(location_query)
```

---

## 📚 9. 참고 자료

- [카카오 로컬 API 공식 문서](https://developers.kakao.com/docs/latest/ko/local/dev-guide)
- [주소 검색 API](https://developers.kakao.com/docs/latest/ko/local/dev-guide#search-by-address)
- [키워드 검색 API](https://developers.kakao.com/docs/latest/ko/local/dev-guide#search-by-keyword)
- [카테고리 코드 목록](https://developers.kakao.com/docs/latest/ko/local/dev-guide#search-by-category-request)

---

## 🧪 10. 전체 테스트 스크립트

```python
"""
카카오 지도 API 테스트 스크립트
파일명: test_kakao_api.py
"""

import os
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

# Tools 모듈 import
from src.utils.tools import hospital_recommend_tool

# 테스트 위치 리스트
test_locations = [
    "서울시 강남구 역삼동",
    "서울시 마포구 상암동",
    "부산시 해운대구",
    "대구시 중구"
]

print("=" * 60)
print("카카오 지도 API 테스트 시작")
print("=" * 60)

for location in test_locations:
    print(f"\n[테스트] 위치: {location}")
    print("-" * 60)
    
    result = hospital_recommend_tool.invoke(location)
    print(result)
    print("-" * 60)

print("\n테스트 완료!")
```

**실행**:

```powershell
python test_kakao_api.py
```

---

**Made with 🗺️ for Pet Health AI**
