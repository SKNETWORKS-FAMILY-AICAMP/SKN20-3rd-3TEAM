"""
병원/지도 질문 처리 핸들러 (타입 B)
JSON 데이터 조회 → Kakao Map API 활용 → 지도 시각화
"""
from typing import Dict, List, Any, Optional
from datetime import datetime
import json
from pathlib import Path
from .base import BaseHandler
from src.external import HospitalMapper
from src.utils import get_logger
from src.config import get_settings

logger = get_logger(__name__)


class HospitalHandler(BaseHandler):
    """병원 정보 처리 핸들러 (JSON 기반)"""
    
    def __init__(self, hospital_json_path: Optional[str] = None):
        """
        Args:
            hospital_json_path: 병원 정보 JSON 파일 경로
        """
        settings = get_settings()
        self.hospital_json_path = hospital_json_path or settings.data.hospital_json_path
        self.hospitals = []
        self.metadata = {}
        self.mapper = HospitalMapper()
        
        # JSON 로드
        self._load_hospital_data()
        
        logger.info(f"HospitalHandler 초기화: {len(self.hospitals)}개 병원")
    
    def _load_hospital_data(self):
        """JSON 파일에서 병원 데이터 로드"""
        try:
            path = Path(self.hospital_json_path)
            if not path.exists():
                logger.warning(f"병원 JSON 파일을 찾을 수 없습니다: {self.hospital_json_path}")
                self.hospitals = []
                return
            
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # JSON 구조에 따라 데이터 파싱
            if isinstance(data, dict):
                self.metadata = data.get('DESCRIPTION', {})
                self.hospitals = data.get('DATA', [])
            elif isinstance(data, list):
                self.hospitals = data
            else:
                self.hospitals = []
            
            logger.info(f"병원 데이터 로드 완료: {len(self.hospitals)}개")
            if self.hospitals:
                logger.debug(f"첫 병원: {self.hospitals[0].get('bplcnm', 'Unknown')}")
        
        except json.JSONDecodeError as e:
            logger.error(f"JSON 파일 파싱 오류: {str(e)}")
            self.hospitals = []
        except Exception as e:
            logger.error(f"병원 데이터 로드 실패: {str(e)}")
            self.hospitals = []
    
    def _extract_location_from_address(self, address: str) -> Dict[str, str]:
        """
        주소에서 지역 정보 추출
        
        Args:
            address: 주소 문자열
            
        Returns:
            {'district': '강남구', 'dong': '삼성동', ...}
        """
        parts = address.split() if address else []
        result = {'address': address}
        
        if len(parts) > 0:
            result['district'] = parts[0]  # 구
        if len(parts) > 1:
            result['dong'] = parts[1]  # 동
        
        return result
    
    def _get_hospital_address(self, hospital: Dict[str, Any]) -> str:
        """
        병원 정보에서 주소 추출
        
        Args:
            hospital: 병원 정보 딕셔너리
            
        Returns:
            주소 문자열
        """
        # 도로명주소 우선, 없으면 지번주소
        address = hospital.get('rdnwhladdr') or hospital.get('sitewhladdr') or 'Unknown'
        return address.strip() if isinstance(address, str) else 'Unknown'
    
    def search_by_location(self, location: str, radius_km: float = 2.0) -> List[Dict[str, Any]]:
        """
        위치 기반 병원 검색
        
        Args:
            location: 검색 위치 (예: "강남구", "삼성동")
            radius_km: 검색 반경 (km)
            
        Returns:
            검색된 병원 리스트
        """
        logger.debug(f"위치 기반 검색: location={location}, radius={radius_km}km")
        
        results = []
        for hospital in self.hospitals:
            # 영업 상태 확인
            if hospital.get('trdstategbn') != '01':
                continue
            
            address = self._get_hospital_address(hospital)
            
            # 주소에서 위치 정보 추출
            if location in address:
                hospital_info = {
                    'name': hospital.get('bplcnm', 'Unknown'),
                    'address': address,
                    'phone': hospital.get('sitetel', ''),
                    'type': hospital.get('bplctp', ''),
                    'operating_status': '영업 중',
                    'distance_km': 0.0
                }
                results.append(hospital_info)
        
        logger.debug(f"검색 완료: {len(results)}개 병원 발견")
        return results
    
    def get_nearby_hospitals(
        self,
        latitude: float,
        longitude: float,
        radius_km: float = 2.0,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        좌표 기반 근처 병원 검색
        
        Args:
            latitude: 위도
            longitude: 경도
            radius_km: 검색 반경
            limit: 반환 개수
            
        Returns:
            근처 병원 리스트
        """
        logger.debug(f"좌표 기반 검색: lat={latitude}, lng={longitude}, radius={radius_km}km")
        
        from math import radians, sin, cos, sqrt, atan2
        
        def haversine(lat1, lon1, lat2, lon2):
            """두 좌표 간 거리 계산 (Haversine 공식)"""
            R = 6371  # 지구 반경 (km)
            
            lat1_rad = radians(lat1)
            lat2_rad = radians(lat2)
            delta_lat = radians(lat2 - lat1)
            delta_lon = radians(lon2 - lon1)
            
            a = sin(delta_lat/2)**2 + cos(lat1_rad) * cos(lat2_rad) * sin(delta_lon/2)**2
            c = 2 * atan2(sqrt(a), sqrt(1-a))
            
            return R * c
        
        results = []
        for hospital in self.hospitals:
            # 영업 상태 확인
            if hospital.get('trdstategbn') != '01':
                continue
            
            # 좌표 확인
            try:
                hosp_lat = float(hospital.get('y', 0))
                hosp_lng = float(hospital.get('x', 0))
                
                if hosp_lat == 0 or hosp_lng == 0:
                    continue
                
                # 거리 계산
                distance = haversine(latitude, longitude, hosp_lat, hosp_lng)
                
                if distance <= radius_km:
                    hospital_info = {
                        'name': hospital.get('bplcnm', 'Unknown'),
                        'address': self._get_hospital_address(hospital),
                        'phone': hospital.get('sitetel', ''),
                        'type': hospital.get('bplctp', ''),
                        'operating_status': '영업 중',
                        'latitude': hosp_lat,
                        'longitude': hosp_lng,
                        'distance_km': round(distance, 2)
                    }
                    results.append(hospital_info)
            
            except (ValueError, TypeError):
                continue
        
        # 거리순 정렬
        results.sort(key=lambda x: x['distance_km'])
        
        logger.debug(f"검색 완료: {len(results)}개 병원 발견")
        return results[:limit]
    
    def handle(self, query: str, **kwargs) -> Dict[str, Any]:
        """
        병원 질문 처리 메인 함수
        
        Args:
            query: 사용자 질문
            **kwargs: 추가 파라미터
                - latitude: 위도
                - longitude: 경도
                - location: 위치명
                
        Returns:
            처리 결과 딕셔너리
        """
        logger.info(f"병원 질문 처리 시작: {query[:50]}...")
        
        result = {
            'question': query,
            'question_type': 'B',
            'timestamp': datetime.now().isoformat(),
            'response': '',
            'hospitals': [],
            'map_url': None
        }
        
        # 위도/경도로 검색
        latitude = kwargs.get('latitude')
        longitude = kwargs.get('longitude')
        
        if latitude and longitude:
            logger.debug("좌표 기반 검색 수행")
            hospitals = self.get_nearby_hospitals(latitude, longitude)
        else:
            # 위치명으로 검색
            location = kwargs.get('location')
            if location:
                logger.debug(f"위치명 기반 검색 수행: {location}")
                hospitals = self.search_by_location(location)
            else:
                # 전체 병원 중 영업 중인 것만 반환
                logger.debug("전체 병원 조회")
                hospitals = [
                    {
                        'name': h.get('bplcnm', 'Unknown'),
                        'address': self._get_hospital_address(h),
                        'phone': h.get('sitetel', ''),
                        'type': h.get('bplctp', ''),
                        'operating_status': '영업 중'
                    }
                    for h in self.hospitals
                    if h.get('trdstategbn') == '01'
                ][:10]
        
        result['hospitals'] = hospitals
        
        # 응답 메시지 생성
        if hospitals:
            result['response'] = f"{len(hospitals)}개의 동물병원을 찾았습니다:\n\n"
            for i, hospital in enumerate(hospitals[:5], 1):
                result['response'] += f"{i}. {hospital['name']}\n"
                result['response'] += f"   주소: {hospital['address']}\n"
                result['response'] += f"   전화: {hospital['phone']}\n\n"
        else:
            result['response'] = "죄송하지만, 해당 지역의 동물병원을 찾을 수 없습니다."
        
        logger.info(f"병원 질문 처리 완료: {len(hospitals)}개 병원")
        return result

