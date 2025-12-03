import requests
import json
import os
from typing import Dict, List, Optional
from dotenv import load_dotenv

# .env 파일에서 환경 변수 로드
load_dotenv()

# 카카오 REST API 키 설정
KAKAO_REST_API_KEY = os.getenv('KAKAO_MAP_API_KEY')

class KakaoMapAPI:
    """카카오 지도 API를 사용하는 클래스"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {
            "Authorization": f"KakaoAK {api_key}"
        }
    
    def search_address(self, address: str) -> Optional[Dict]:
        """
        주소로 좌표 검색
        
        Args:
            address: 검색할 주소
            
        Returns:
            좌표 정보가 담긴 딕셔너리
        """
        url = "https://dapi.kakao.com/v2/local/search/address.json"
        params = {"query": address}
        
        response = requests.get(url, headers=self.headers, params=params)
        
        if response.status_code == 200:
            result = response.json()
            if result['documents']:
                return result['documents'][0]
        return None
    
    def search_keyword(self, keyword: str, x: float = None, y: float = None, radius: int = None) -> List[Dict]:
        """
        키워드로 장소 검색
        
        Args:
            keyword: 검색할 키워드
            x: 중심 좌표의 경도 (선택)
            y: 중심 좌표의 위도 (선택)
            radius: 검색 반경(미터) (선택, 최대 20000)
            
        Returns:
            검색 결과 리스트
        """
        url = "https://dapi.kakao.com/v2/local/search/keyword.json"
        params = {"query": keyword}
        
        if x and y:
            params['x'] = x
            params['y'] = y
        if radius:
            params['radius'] = radius
            
        response = requests.get(url, headers=self.headers, params=params)
        
        if response.status_code == 200:
            result = response.json()
            return result['documents']
        return []
    
    def coord_to_address(self, x: float, y: float) -> Optional[Dict]:
        """
        좌표를 주소로 변환
        
        Args:
            x: 경도
            y: 위도
            
        Returns:
            주소 정보가 담긴 딕셔너리
        """
        url = "https://dapi.kakao.com/v2/local/geo/coord2address.json"
        params = {"x": x, "y": y}
        
        response = requests.get(url, headers=self.headers, params=params)
        
        if response.status_code == 200:
            result = response.json()
            if result['documents']:
                return result['documents'][0]
        return None
    
    def search_category(self, category_code: str, x: float, y: float, radius: int = 1000) -> List[Dict]:
        """
        카테고리로 장소 검색
        
        Args:
            category_code: 카테고리 코드 (예: CE7-카페, FD6-음식점, HP8-병원, PM9-약국 등)
            x: 중심 좌표의 경도
            y: 중심 좌표의 위도
            radius: 검색 반경(미터, 최대 20000)
            
        Returns:
            검색 결과 리스트
        """
        url = "https://dapi.kakao.com/v2/local/search/category.json"
        params = {
            "category_group_code": category_code,
            "x": x,
            "y": y,
            "radius": radius
        }
        
        response = requests.get(url, headers=self.headers, params=params)
        
        if response.status_code == 200:
            result = response.json()
            return result['documents']
        return []
    
    def get_distance(self, origin_x: float, origin_y: float, dest_x: float, dest_y: float) -> float:
        """
        두 좌표 간의 직선 거리 계산 (Haversine 공식)
        
        Args:
            origin_x: 출발지 경도
            origin_y: 출발지 위도
            dest_x: 목적지 경도
            dest_y: 목적지 위도
            
        Returns:
            거리(미터)
        """
        from math import radians, sin, cos, sqrt, atan2
        
        R = 6371000  # 지구 반경(미터)
        
        lat1 = radians(origin_y)
        lat2 = radians(dest_y)
        delta_lat = radians(dest_y - origin_y)
        delta_lon = radians(dest_x - origin_x)
        
        a = sin(delta_lat/2)**2 + cos(lat1) * cos(lat2) * sin(delta_lon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        
        distance = R * c
        return distance


def main():
    """메인 함수 - 사용 예시"""
    
    # API 인스턴스 생성
    kakao_api = KakaoMapAPI(KAKAO_REST_API_KEY)
    
    print("=" * 50)
    print("🗺️  카카오 지도 API 사용 예시")
    print("=" * 50)
    
    # 1. 주소로 좌표 검색
    print("\n1️⃣  주소로 좌표 검색")
    address = "서울특별시 중구 세종대로 110"  # 서울시청
    result = kakao_api.search_address(address)
    if result:
        print(f"주소: {result['address_name']}")
        print(f"좌표: ({result['y']}, {result['x']})")
        seoul_x, seoul_y = float(result['x']), float(result['y'])
    
    # 2. 키워드로 장소 검색
    print("\n2️⃣  키워드로 장소 검색")
    keyword = "강남역 카페"
    places = kakao_api.search_keyword(keyword)
    if places:
        print(f"'{keyword}' 검색 결과 ({len(places)}개):")
        for i, place in enumerate(places[:5], 1):
            print(f"  {i}. {place['place_name']}")
            print(f"     주소: {place['address_name']}")
            print(f"     좌표: ({place['y']}, {place['x']})")
    
    # 3. 좌표를 주소로 변환
    print("\n3️⃣  좌표를 주소로 변환")
    x, y = 126.9780, 37.5665  # 서울시청 좌표
    address_info = kakao_api.coord_to_address(x, y)
    if address_info:
        print(f"좌표: ({y}, {x})")
        if 'address' in address_info:
            print(f"지번 주소: {address_info['address']['address_name']}")
        if 'road_address' in address_info:
            print(f"도로명 주소: {address_info['road_address']['address_name']}")
    
    # 4. 카테고리로 검색 (서울시청 근처 카페)
    print("\n4️⃣  카테고리로 장소 검색 (서울시청 근처 카페)")
    cafes = kakao_api.search_category("CE7", 126.9780, 37.5665, radius=500)
    if cafes:
        print(f"반경 500m 내 카페 ({len(cafes)}개):")
        for i, cafe in enumerate(cafes[:5], 1):
            print(f"  {i}. {cafe['place_name']}")
            print(f"     거리: {cafe['distance']}m")
    
    # 5. 두 지점 간 거리 계산
    print("\n5️⃣  두 지점 간 거리 계산")
    # 서울시청과 강남역 사이 거리
    gangnam = kakao_api.search_keyword("강남역")
    if gangnam:
        gangnam_x, gangnam_y = float(gangnam[0]['x']), float(gangnam[0]['y'])
        distance = kakao_api.get_distance(126.9780, 37.5665, gangnam_x, gangnam_y)
        print(f"서울시청 → 강남역")
        print(f"직선 거리: {distance/1000:.2f}km")
    
    print("\n" + "=" * 50)


if __name__ == "__main__":
    # 필요한 라이브러리 설치
    # pip install requests python-dotenv
    
    # API 키 확인
    if not KAKAO_REST_API_KEY:
        print("❌ .env 파일에 KAKAO_MAP_API_KEY가 설정되지 않았습니다!")
        print("💡 .env 파일을 생성하고 다음과 같이 설정하세요:")
        print("   KAKAO_MAP_API_KEY=your_api_key_here")
        exit(1)
    
    try:
        main()
    except requests.exceptions.RequestException as e:
        print(f"❌ API 요청 중 오류 발생: {e}")
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        print("\n💡 .env 파일의 REST API 키를 확인하세요!")
