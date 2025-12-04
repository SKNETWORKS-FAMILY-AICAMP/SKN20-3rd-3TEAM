"""
병원 위치 매핑 모듈

지역/위치 텍스트로부터 병원 정보와 좌표를 추출하고 반환합니다.
"""

import re
from typing import Any, Dict, List, Optional, Tuple

from src.config.logger import get_logger
from src.config.settings import settings
from src.utils.helpers import extract_keywords

logger = get_logger(__name__)


class HospitalMapper:
    """
    병원 위치 매퍼

    질문 텍스트에서 위치 정보를 추출하고, 해당 위치의 병원 정보를 반환합니다.

    Note:
        현재는 placeholder 형태로 구현되었으며, 다음과 같이 확장 가능:
        1. 실제 카카오맵 API 연동
        2. 위치 정보 NER (Named Entity Recognition)
        3. 병원 정보 데이터베이스
        4. 거리 계산 알고리즘
    """

    # 대한민국 주요 지역 좌표 맵
    REGION_COORDINATES = {
        "강남": {"lat": 37.4979, "lon": 127.0276},
        "강남구": {"lat": 37.4979, "lon": 127.0276},
        "강북": {"lat": 37.6403, "lon": 127.0265},
        "강북구": {"lat": 37.6403, "lon": 127.0265},
        "서초": {"lat": 37.4847, "lon": 127.0331},
        "서초구": {"lat": 37.4847, "lon": 127.0331},
        "서울": {"lat": 37.5665, "lon": 126.9780},
        "부산": {"lat": 35.1796, "lon": 129.0756},
        "대구": {"lat": 35.8715, "lon": 128.6030},
        "인천": {"lat": 37.4563, "lon": 126.7056},
        "대전": {"lat": 36.3504, "lon": 127.3845},
    }

    # 위치 관련 키워드
    LOCATION_KEYWORDS = [
        "위치", "지도", "근처", "주소", "어디", "찾기", "길", "이웃", "옆",
    ]

    def __init__(self, kakao_api_key: str = settings.KAKAO_MAP_API_KEY):
        """
        병원 위치 매퍼 초기화

        Args:
            kakao_api_key: 카카오맵 API 키
        """
        self.kakao_api_key = kakao_api_key
        logger.info("HospitalMapper initialized")

    def extract_and_search(
        self, query: str
    ) -> Dict[str, Any]:
        """
        질문 텍스트에서 위치를 추출하고 병원을 검색합니다.

        Args:
            query: 사용자 질문 (예: "강남역 근처 동물병원")

        Returns:
            Dict: 위치 정보와 병원 검색 결과

        Note:
            반환 구조:
            {
                "location": {"region": "강남", "landmark": "강남역"},
                "coordinates": {"lat": 37.4979, "lon": 127.0276},
                "hospitals": [...],
                "success": bool
            }
        """
        logger.info(f"Extracting location from: '{query}'")

        try:
            # 1. 질문에서 위치 정보 추출
            location_info = self._extract_location(query)

            if not location_info["region"]:
                logger.warning("Could not extract location from query")
                return {
                    "location": location_info,
                    "coordinates": None,
                    "hospitals": [],
                    "success": False,
                    "error": "위치 정보를 추출할 수 없습니다.",
                }

            # 2. 위치 정보로부터 좌표 획득
            coordinates = self._get_coordinates(location_info)

            # 3. 좌표 기반 병원 검색
            hospitals = self._search_hospitals_nearby(
                coordinates, location_info
            )

            result = {
                "location": location_info,
                "coordinates": coordinates,
                "hospitals": hospitals,
                "success": True,
            }

            logger.info(
                f"Found {len(hospitals)} hospitals near {location_info['region']}"
            )
            return result

        except Exception as e:
            logger.error(f"Location extraction failed: {str(e)}")
            return {
                "location": None,
                "coordinates": None,
                "hospitals": [],
                "success": False,
                "error": str(e),
            }

    def extract_location(self, text: str) -> Dict[str, Optional[str]]:
        """
        텍스트에서 위치 정보를 추출합니다.

        Args:
            text: 분석할 텍스트

        Returns:
            Dict: 추출된 위치 정보
                - region: 지역 (시, 도)
                - district: 구
                - landmark: 랜드마크 (역, 거리 등)
                - address: 주소
        """
        return self._extract_location(text)

    def get_distance(
        self, lat1: float, lon1: float, lat2: float, lon2: float
    ) -> float:
        """
        두 좌표 사이의 거리를 계산합니다 (Haversine 공식).

        Args:
            lat1, lon1: 첫 번째 좌표
            lat2, lon2: 두 번째 좌표

        Returns:
            float: 거리 (미터)
        """
        import math

        R = 6371000  # 지구 반지름 (m)

        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)

        a = (
            math.sin(delta_lat / 2) ** 2
            + math.cos(lat1_rad)
            * math.cos(lat2_rad)
            * math.sin(delta_lon / 2) ** 2
        )
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        distance = R * c
        return distance

    def _extract_location(self, text: str) -> Dict[str, Optional[str]]:
        """
        텍스트에서 위치 정보를 추출합니다 (내부 메서드).

        Args:
            text: 분석할 텍스트

        Returns:
            Dict: 추출된 위치 정보
        """
        location_info = {
            "region": None,
            "district": None,
            "landmark": None,
            "address": None,
        }

        # 알려진 지역 키워드로 검색
        for region, coords in self.REGION_COORDINATES.items():
            if region in text:
                location_info["region"] = region
                break

        # 랜드마크 추출 (예: "강남역", "논현역" 등)
        landmark_pattern = r"(\w+역|\w+로|\w+길|\w+거리)"
        landmark_matches = re.findall(landmark_pattern, text)
        if landmark_matches:
            location_info["landmark"] = landmark_matches[0]

        # 주소 형식 추출 (시/도, 구, 동)
        address_pattern = (
            r"([가-힣]+시|[가-힣]+도)\s+([가-힣]+구|[가-힣]+군)\s+([가-힣]+동)"
        )
        address_matches = re.search(address_pattern, text)
        if address_matches:
            location_info["region"] = address_matches.group(1)
            location_info["district"] = address_matches.group(2)

        return location_info

    def _get_coordinates(self, location_info: Dict[str, Optional[str]]) -> Optional[Dict[str, float]]:
        """
        위치 정보로부터 좌표를 획득합니다 (내부 메서드).

        Args:
            location_info: 위치 정보

        Returns:
            Optional[Dict]: 좌표 정보 또는 None
        """
        region = location_info.get("region")

        if not region:
            return None

        # 알려진 좌표가 있으면 반환
        if region in self.REGION_COORDINATES:
            return self.REGION_COORDINATES[region]

        # TODO: 카카오맵 API로 좌표 검색
        # response = requests.get(
        #     "https://dapi.kakao.com/v2/local/search/address.json",
        #     headers={"Authorization": f"KakaoAK {self.kakao_api_key}"},
        #     params={"query": region}
        # )

        logger.warning(f"Could not find coordinates for region: {region}")
        return None

    def _search_hospitals_nearby(
        self, coordinates: Dict[str, float], location_info: Dict[str, Optional[str]]
    ) -> List[Dict[str, Any]]:
        """
        좌표 근처의 병원을 검색합니다 (내부 메서드).

        Args:
            coordinates: 검색 중심 좌표
            location_info: 위치 정보

        Returns:
            List[Dict]: 병원 정보 리스트

        Note:
            현재는 mock 데이터를 반환합니다.
            실제 구현 시:
            1. 카카오맵 Places 검색 API 호출
            2. 병원 정보 DB에서 조회
            3. 거리 계산 후 정렬
        """
        if not coordinates:
            return []

        # TODO: 실제 병원 검색 구현
        # response = kakao_places_api.search(
        #     query="동물병원",
        #     x=coordinates["lon"],
        #     y=coordinates["lat"],
        #     radius=5000  # 5km
        # )

        # 현재는 mock 데이터 반환
        region = location_info.get("region", "unknown")
        mock_hospitals = [
            {
                "name": f"{region} ABC 동물병원",
                "address": f"{region}구 테헤란로 123",
                "phone": "02-1234-5678",
                "distance": 500,
                "lat": coordinates["lat"] + 0.001,
                "lon": coordinates["lon"] + 0.001,
            },
            {
                "name": f"{region} 펫케어 클리닉",
                "address": f"{region}구 남부순환로 456",
                "phone": "02-2222-3333",
                "distance": 1200,
                "lat": coordinates["lat"] - 0.001,
                "lon": coordinates["lon"] - 0.001,
            },
        ]

        return mock_hospitals

