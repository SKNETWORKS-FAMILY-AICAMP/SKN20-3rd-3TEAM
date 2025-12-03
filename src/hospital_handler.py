"""
병원/지도 질문 처리 모듈 (타입 B)
JSON 데이터 조회 → Kakao Map API 활용 → 지도 시각화
"""
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path

# requests는 선택적 의존성
try:
    import requests
except ImportError:
    requests = None


class HospitalHandler:
    """병원 정보 처리 핸들러 (JSON 기반)"""
    
    def __init__(self, hospital_json_path: str = "data/raw/hospital/서울시_동물병원_인허가_정보.json"):
        """
        Args:
            hospital_json_path: 병원 정보 JSON 파일 경로
        """
        self.hospital_json_path = hospital_json_path
        self.hospitals = []
        self.metadata = {}
        self.kakao_api_key = None
        
        # JSON 로드
        self._load_hospital_data()
    
    def _load_hospital_data(self):
        """JSON 파일에서 병원 데이터 로드"""
        try:
            with open(self.hospital_json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # JSON 구조에 따라 데이터 파싱
            if isinstance(data, dict):
                self.metadata = data.get('DESCRIPTION', {})
                self.hospitals = data.get('DATA', [])
            elif isinstance(data, list):
                self.hospitals = data
            else:
                self.hospitals = []
            
            print(f"✓ 병원 데이터 로드 완료: {len(self.hospitals)}개 병원")
            if self.hospitals:
                print(f"  첫 병원: {self.hospitals[0].get('bplcnm', 'Unknown')}")
        except FileNotFoundError:
            print(f"❌ JSON 파일을 찾을 수 없습니다: {self.hospital_json_path}")
            self.hospitals = []
        except json.JSONDecodeError as e:
            print(f"❌ JSON 파일 파싱 오류: {e}")
            self.hospitals = []
        except Exception as e:
            print(f"❌ 병원 데이터 로드 실패: {e}")
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
        # JSON 데이터의 주소 필드 (도로명주소 우선)
        address = hospital.get('rdnwhladdr') or hospital.get('sitewhladdr') or 'Unknown'
        return address.strip() if isinstance(address, str) else 'Unknown'
    
    def search_by_location(self, location: str, radius_km: float = 2.0) -> List[Dict[str, Any]]:
        """
        위치 기반 병원 검색
        
        Args:
            location: 검색 위치 (예: "강남구", "삼성동")
            radius_km: 검색 반경 (km)
            
        Returns:
            병원 정보 리스트
        """
        if not self.hospitals or len(self.hospitals) == 0:
            return []
        
        hospitals = []
        location_lower = location.lower()
        
        for hospital in self.hospitals:
            address = self._get_hospital_address(hospital)
            address_lower = address.lower()
            
            # 정확한 위치 기반 필터링: 주소에 검색어가 포함되어야 함
            if location_lower in address_lower:
                # 영업 중인 병원만 포함
                status = hospital.get('trdstatenm', '')
                if '폐업' in status or '폐지' in status:
                    continue
                
                hospital_info = {
                    'name': hospital.get('bplcnm', 'Unknown'),
                    'address': address,
                    'phone': hospital.get('sitetel', 'Unknown'),
                    'district': location,
                    'status': status,
                    'state': hospital.get('dtlstatenm', 'Unknown'),
                    'coordinates': {
                        'x': hospital.get('x', 'N/A'),
                        'y': hospital.get('y', 'N/A')
                    },
                    'original_data': hospital
                }
                hospitals.append(hospital_info)
        
        return hospitals
    
    def search_by_name(self, hospital_name: str) -> List[Dict[str, Any]]:
        """
        병원명으로 검색
        
        Args:
            hospital_name: 병원명 또는 부분명
            
        Returns:
            병원 정보 리스트
        """
        if not self.hospitals or len(self.hospitals) == 0:
            return []
        
        hospitals = []
        hospital_name_lower = hospital_name.lower()
        
        for hospital in self.hospitals:
            name = hospital.get('bplcnm', '').lower()
            
            # 병원명 기반 필터링
            if hospital_name_lower in name:
                address = self._get_hospital_address(hospital)
                
                hospital_info = {
                    'name': hospital.get('bplcnm', 'Unknown'),
                    'address': address,
                    'phone': hospital.get('sitetel', 'Unknown'),
                    'status': hospital.get('trdstatenm', 'Unknown'),
                    'state': hospital.get('dtlstatenm', 'Unknown'),
                    'approval_date': hospital.get('apvpermymd', 'N/A'),
                    'coordinates': {
                        'x': hospital.get('x', 'N/A'),
                        'y': hospital.get('y', 'N/A')
                    },
                    'original_data': hospital
                }
                hospitals.append(hospital_info)
        
        return hospitals
    
    def get_nearby_hospitals(self, district: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        특정 구의 동물병원 목록 조회
        
        Args:
            district: 구명 (예: "강남구")
            limit: 반환 개수 제한
            
        Returns:
            병원 정보 리스트 (최대 limit개)
        """
        hospitals = self.search_by_location(district)
        
        # 검색된 병원 수를 알려주고 제한된 개수만 반환
        print(f"  찾은 병원: {len(hospitals)}개 중 상위 {min(limit, len(hospitals))}개 반환")
        
        return hospitals[:limit]
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        병원 데이터 통계
        
        Returns:
            통계 정보
        """
        if not self.hospitals or len(self.hospitals) == 0:
            return {}
        
        # 구 기준 병원 수 및 영업 상태
        district_counts = {}
        status_counts = {}
        operating_hospitals = 0
        closed_hospitals = 0
        
        for hospital in self.hospitals:
            address = self._get_hospital_address(hospital)
            
            # 구 정보 추출
            parts = address.split() if address else []
            if parts and '구' in parts[0]:
                district = parts[0]
                district_counts[district] = district_counts.get(district, 0) + 1
            
            # 영업 상태 집계
            status = hospital.get('trdstatenm', 'Unknown')
            status_counts[status] = status_counts.get(status, 0) + 1
            
            if '영업' in status:
                operating_hospitals += 1
            elif '폐업' in status:
                closed_hospitals += 1
        
        return {
            'total_hospitals': len(self.hospitals),
            'operating_hospitals': operating_hospitals,
            'closed_hospitals': closed_hospitals,
            'districts': district_counts,
            'status_distribution': status_counts,
            'top_districts': sorted(
                district_counts.items(),
                key=lambda x: x[1],
                reverse=True
            )[:10]
        }
    
    def format_hospital_info(self, hospital: Dict[str, Any]) -> str:
        """
        병원 정보 포맷팅
        
        Args:
            hospital: 병원 정보 딕셔너리
            
        Returns:
            포맷된 문자열
        """
        info = f"""
🏥 {hospital.get('name', 'Unknown')}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📍 주소: {hospital.get('address', 'Unknown')}
📞 전화: {hospital.get('phone', 'Unknown')}
상태: {hospital.get('status', 'Unknown')}
영업형태: {hospital.get('business_type', 'Unknown')}
"""
        return info
    
    def handle_hospital_question(self, query: str) -> Dict[str, Any]:
        """
        병원 관련 질문 처리 메인 함수
        
        Args:
            query: 사용자 질문
            
        Returns:
            처리 결과 딕셔너리
        """
        print(f"\n[병원 질문 처리] {query}")
        print("-" * 60)
        
        result = {
            'question': query,
            'question_type': 'B',
            'timestamp': datetime.now().isoformat(),
            'hospitals': [],
            'statistics': {},
            'response': ''
        }
        
        # 질문 분석 및 검색 수행
        import re
        query_lower = query.lower()
        
        # 지역명(구) 추출 - 우선 처리
        district_match = re.search(r'([가-힣]+구)', query)
        district = district_match.group(1) if district_match else None
        
        # 1. 지역명이 있으면 해당 지역 검색 (최우선)
        if district:
            print(f"지역 검색: {district}")
            hospitals = self.get_nearby_hospitals(district, limit=10)
            result['hospitals'] = hospitals
        
        # 2. 지역명이 없으면 특정 병원명으로 검색
        elif any(keyword in query for keyword in ['병원', '수의사', '진료소']):
            hospital_name_match = re.search(r'([가-힣\w]+)\s*(병원|수의사|진료소)', query)
            
            if hospital_name_match:
                hospital_name = hospital_name_match.group(1)
                print(f"병원명 검색: {hospital_name}")
                hospitals = self.search_by_name(hospital_name)
                result['hospitals'] = hospitals
        
        # 3. 병원 정보 요청
        elif any(keyword in query for keyword in ['정보', '목록', '찾기', '검색']):
            stats = self.get_statistics()
            result['statistics'] = stats
            result['hospitals'] = self._get_top_hospitals(5)
        
        # 응답 생성
        response_lines = []
        
        if result['hospitals']:
            response_lines.append(f"🔍 검색 결과: {len(result['hospitals'])}개 병원 발견\n")
            for i, hospital in enumerate(result['hospitals'][:10], 1):
                response_lines.append(f"{i}. {self.format_hospital_info(hospital)}")
        
        if result['statistics']:
            response_lines.append("\n📊 병원 통계:")
            response_lines.append(f"총 병원 수: {result['statistics']['total_hospitals']}")
            response_lines.append("\n구별 병원 수 (상위 10개):")
            for district, count in result['statistics']['top_districts']:
                response_lines.append(f"  • {district}: {count}개")
        
        if not result['hospitals'] and not result['statistics']:
            response_lines.append("검색 결과가 없습니다. 다른 검색 조건을 시도해주세요.")
        
        result['response'] = "\n".join(response_lines)
        
        return result
    
    def _get_top_hospitals(self, limit: int = 5) -> List[Dict[str, Any]]:
        """상위 병원 정보 조회"""
        if not self.hospitals or len(self.hospitals) == 0:
            return []
        
        hospitals = []
        for hospital in self.hospitals[:limit]:
            address = self._get_hospital_address(hospital)
            
            hospital_info = {
                'name': hospital.get('bplcnm', 'Unknown'),
                'address': address,
                'phone': hospital.get('sitetel', 'Unknown'),
                'status': hospital.get('trdstatenm', 'Unknown'),
                'state': hospital.get('dtlstatenm', 'Unknown'),
                'approval_date': hospital.get('apvpermymd', 'N/A'),
                'coordinates': {
                    'x': hospital.get('x', 'N/A'),
                    'y': hospital.get('y', 'N/A')
                }
            }
            hospitals.append(hospital_info)
        
        return hospitals
    
    def search_by_coordinates(self, x: float, y: float, radius: float = 1.0) -> List[Dict[str, Any]]:
        """
        좌표 기반 병원 검색 (반경 내 병원)
        
        Args:
            x: X 좌표 (경도)
            y: Y 좌표 (위도)
            radius: 검색 반경 (대략적 거리 단위)
            
        Returns:
            병원 정보 리스트
        """
        if not self.hospitals:
            return []
        
        hospitals = []
        for hospital in self.hospitals:
            try:
                hosp_x = float(hospital.get('x', 0))
                hosp_y = float(hospital.get('y', 0))
                
                # 간단한 거리 계산 (피타고라스 정리)
                distance = ((hosp_x - x) ** 2 + (hosp_y - y) ** 2) ** 0.5
                
                if distance <= radius:
                    address = self._get_hospital_address(hospital)
                    hospital_info = {
                        'name': hospital.get('bplcnm', 'Unknown'),
                        'address': address,
                        'phone': hospital.get('sitetel', 'Unknown'),
                        'status': hospital.get('trdstatenm', 'Unknown'),
                        'state': hospital.get('dtlstatenm', 'Unknown'),
                        'coordinates': {
                            'x': hosp_x,
                            'y': hosp_y
                        },
                        'distance': distance
                    }
                    hospitals.append(hospital_info)
            except (ValueError, TypeError):
                continue
        
        # 거리 순으로 정렬
        hospitals.sort(key=lambda x: x.get('distance', float('inf')))
        return hospitals
    
    def export_to_json(self, output_path: str = "hospitals_export.json") -> bool:
        """
        병원 데이터를 JSON으로 내보내기
        
        Args:
            output_path: 출력 파일 경로
            
        Returns:
            성공 여부
        """
        try:
            export_data = {
                'metadata': {
                    'total_hospitals': len(self.hospitals),
                    'export_date': datetime.now().isoformat(),
                    'data_source': self.hospital_json_path
                },
                'hospitals': []
            }
            
            for hospital in self.hospitals:
                hospital_export = {
                    'name': hospital.get('bplcnm', 'Unknown'),
                    'address': self._get_hospital_address(hospital),
                    'phone': hospital.get('sitetel', 'Unknown'),
                    'status': hospital.get('trdstatenm', 'Unknown'),
                    'approval_date': hospital.get('apvpermymd', 'N/A'),
                    'coordinates': {
                        'x': hospital.get('x', 'N/A'),
                        'y': hospital.get('y', 'N/A')
                    }
                }
                export_data['hospitals'].append(hospital_export)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)
            
            print(f"✓ 병원 데이터를 {output_path}로 내보냈습니다.")
            return True
        except Exception as e:
            print(f"❌ 내보내기 실패: {e}")
            return False
    
    def get_operating_hospitals_by_district(self, district: str) -> List[Dict[str, Any]]:
        """
        특정 구의 영업 중인 병원 목록 조회
        
        Args:
            district: 구명
            
        Returns:
            영업 중인 병원 정보 리스트
        """
        if not self.hospitals:
            return []
        
        hospitals = []
        for hospital in self.hospitals:
            address = self._get_hospital_address(hospital)
            status = hospital.get('trdstatenm', '')
            
            # 해당 구이고 영업 상태인 병원
            if district in address and '영업' in status:
                hospital_info = {
                    'name': hospital.get('bplcnm', 'Unknown'),
                    'address': address,
                    'phone': hospital.get('sitetel', 'Unknown'),
                    'status': status,
                    'approval_date': hospital.get('apvpermymd', 'N/A'),
                    'coordinates': {
                        'x': hospital.get('x', 'N/A'),
                        'y': hospital.get('y', 'N/A')
                    }
                }
                hospitals.append(hospital_info)
        
        return hospitals
    
    def get_hospital_metadata_description(self) -> Dict[str, str]:
        """
        병원 데이터의 메타데이터 설명 반환
        
        Returns:
            필드 설명 딕셔너리
        """
        return self.metadata

