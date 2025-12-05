"""
app/maps_client.py
카카오 맵 API를 사용한 동물병원 검색
"""
import os
import requests
from typing import Optional, List, Dict

# 🔧 config.py에서 settings 가져오기
from app.config import settings

# 🔧 변경: os.getenv 대신 settings 사용
KAKAO_API_KEY = settings.KAKAO_REST_API_KEY

def get_coordinates(address: str) -> Optional[tuple]:
    """
    카카오 API를 사용하여 주소를 좌표로 변환
    
    Args:
        address: 검색할 주소 (상세 주소 포함 가능)
        
    Returns:
        (위도, 경도) 튜플 또는 None
    """
    if not KAKAO_API_KEY:
        print("❌ KAKAO_REST_API_KEY가 설정되지 않았습니다.")
        print("💡 .env 파일에 KAKAO_REST_API_KEY=your_key 형식으로 추가하세요.")
        return None
    
    url = "https://dapi.kakao.com/v2/local/search/address.json"
    headers = {"Authorization": f"KakaoAK {KAKAO_API_KEY}"}
    params = {"query": address}
    
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        
        if data.get("documents"):
            # 첫 번째 결과의 좌표 반환
            doc = data["documents"][0]
            lat = float(doc["y"])  # 위도
            lon = float(doc["x"])  # 경도
            print(f"✅ 좌표 변환 성공: {address} → 위도={lat}, 경도={lon}")
            return (lat, lon)
        else:
            print(f"⚠️ 주소를 찾을 수 없습니다: {address}")
            return None
            
    except Exception as e:
        print(f"❌ 좌표 변환 실패: {e}")
        return None


def search_nearby_hospitals(location: str, radius: int = 3000) -> str:
    """
    카카오 로컬 API를 사용하여 지정된 위치 근처의 동물병원을 검색합니다.
    상세 주소(번지수 포함)를 입력하면 해당 위치 기준 반경 내 동물병원을 검색합니다.
    
    Args:
        location: 검색할 위치 (예: "서울시 송파구 방이동 12-3")
        radius: 검색 반경 (미터 단위, 기본값 3000m = 3km)
    
    Returns:
        동물병원 정보 문자열
    """
    if not KAKAO_API_KEY:
        return "❌ KAKAO_REST_API_KEY가 설정되지 않았습니다.\n💡 .env 파일에 KAKAO_REST_API_KEY=your_key 형식으로 추가하세요."
    
    print(f"🔍 검색 시작: 위치='{location}', 반경={radius}m")
    print(f"🔑 API 키 확인: {KAKAO_API_KEY[:10]}... (앞 10자)")
    
    # 1단계: 주소를 좌표로 변환
    coords = get_coordinates(location)
    
    if not coords:
        # 좌표 변환 실패 시 키워드 검색으로 폴백
        print(f"⚠️ 좌표 변환 실패, 키워드 검색으로 전환: {location}")
        return search_by_keyword(location)
    
    # 2단계: 좌표 기반으로 동물병원 검색
    url = "https://dapi.kakao.com/v2/local/search/keyword.json"
    headers = {"Authorization": f"KakaoAK {KAKAO_API_KEY}"}
    params = {
        "query": "동물병원",
        "y": coords[0],  # 위도
        "x": coords[1],  # 경도
        "radius": radius,  # 반경 (미터)
        "sort": "distance",  # 거리순 정렬
        "size": 10  # 최대 10개 결과
    }
    
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        
        documents = data.get("documents", [])
        
        if not documents:
            return f"❌ '{location}' 기준 반경 {radius}m 내에서 동물병원을 찾을 수 없습니다.\n더 넓은 범위로 검색해보세요."
        
        # 결과 포맷팅
        result = [f"📍 **{location} 기준 반경 {radius}m({radius/1000:.1f}km) 내 동물병원 {len(documents)}곳**\n"]
        
        for i, place in enumerate(documents, 1):
            name = place.get("place_name", "이름 없음")
            address = place.get("road_address_name") or place.get("address_name", "주소 없음")
            phone = place.get("phone", "전화번호 없음")
            distance = place.get("distance", "")
            
            result.append(f"\n**{i}. {name}**")
            result.append(f"   - 주소: {address}")
            result.append(f"   - 전화: {phone}")
            if distance:
                distance_m = int(distance)
                if distance_m < 1000:
                    result.append(f"   - 거리: {distance_m}m")
                else:
                    result.append(f"   - 거리: {distance_m/1000:.1f}km")
        
        return "\n".join(result)
        
    except requests.exceptions.RequestException as e:
        return f"❌ API 요청 중 오류가 발생했습니다: {str(e)}"
    except Exception as e:
        return f"❌ 동물병원 검색 중 오류가 발생했습니다: {str(e)}"


def search_by_keyword(location: str) -> str:
    """
    키워드 기반 동물병원 검색 (좌표 변환 실패 시 폴백)
    
    Args:
        location: 검색할 위치
        
    Returns:
        동물병원 정보 문자열
    """
    url = "https://dapi.kakao.com/v2/local/search/keyword.json"
    headers = {"Authorization": f"KakaoAK {KAKAO_API_KEY}"}
    params = {
        "query": f"{location} 동물병원",
        "size": 10
    }
    
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        
        documents = data.get("documents", [])
        
        if not documents:
            return f"❌ '{location}' 근처에서 동물병원을 찾을 수 없습니다."
        
        result = [f"📍 **{location} 근처 동물병원 {len(documents)}곳**\n"]
        
        for i, place in enumerate(documents, 1):
            name = place.get("place_name", "이름 없음")
            address = place.get("road_address_name") or place.get("address_name", "주소 없음")
            phone = place.get("phone", "전화번호 없음")
            
            result.append(f"\n**{i}. {name}**")
            result.append(f"   - 주소: {address}")
            result.append(f"   - 전화: {phone}")
        
        return "\n".join(result)
        
    except Exception as e:
        return f"❌ 동물병원 검색 중 오류가 발생했습니다: {str(e)}"