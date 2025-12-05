"""
카카오맵 외부 API 통합 모듈
병원 정보를 카카오맵으로 시각화
"""
import os
import json
from typing import Dict, List, Optional
from src.config import get_settings
from src.utils import get_logger

logger = get_logger(__name__)


class HospitalMapper:
    """병원 정보를 카카오맵에 표시하는 클래스"""
    
    def __init__(self, kakao_api_key: Optional[str] = None):
        """
        초기화
        
        Args:
            kakao_api_key: 카카오맵 REST API 키
        """
        settings = get_settings()
        self.kakao_api_key = kakao_api_key or settings.external_api.kakao_map_api_key
        
        if not self.kakao_api_key:
            logger.warning("카카오맵 API 키가 설정되지 않았습니다")
        else:
            logger.info("HospitalMapper 초기화 완료")
    
    def get_hospital_info(self, hospital: Dict) -> Dict:
        """
        병원 정보 추출 및 정규화
        
        Args:
            hospital: 병원 데이터
            
        Returns:
            정규화된 병원 정보
        """
        return {
            'name': hospital.get('bplcnm', '미지정'),
            'address': hospital.get('rdnwhladdr', hospital.get('sitewhladdr', '')),
            'phone': hospital.get('sitetel', ''),
            'lat': float(hospital.get('y', 0)) if hospital.get('y') else None,
            'lng': float(hospital.get('x', 0)) if hospital.get('x') else None,
            'status': '영업 중' if hospital.get('trdstategbn') == '01' else '폐업',
        }
    
    def create_kakao_map_html(
        self,
        hospitals: List[Dict],
        center_lat: float = 37.5665,
        center_lng: float = 126.9780,
        zoom_level: int = 5
    ) -> str:
        """
        카카오맵 HTML 생성
        
        Args:
            hospitals: 병원 정보 리스트
            center_lat: 중심 위도 (기본: 서울)
            center_lng: 중심 경도 (기본: 서울)
            zoom_level: 줌 레벨
            
        Returns:
            카카오맵 HTML 코드
        """
        if not self.kakao_api_key:
            logger.warning("카카오맵 API 키 없음")
            return ""
        
        # 마커 데이터 생성
        markers = []
        for hospital in hospitals:
            info = self.get_hospital_info(hospital)
            if info['lat'] and info['lng']:
                markers.append(info)
        
        # 마커 JSON 생성
        markers_json = json.dumps(markers, ensure_ascii=False)
        
        # HTML 템플릿
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>동물병원 지도</title>
    <script type="text/javascript" src="//dapi.kakao.com/v2/maps/sdk.js?appkey={self.kakao_api_key}"></script>
    <style>
        html, body {{
            width: 100%;
            height: 100%;
            margin: 0;
            padding: 0;
        }}
        #map {{
            width: 100%;
            height: 100%;
        }}
        .info-window {{
            padding: 12px;
            border-radius: 4px;
            background-color: #fff;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .info-window-title {{
            font-weight: bold;
            margin-bottom: 5px;
        }}
        .info-window-content {{
            font-size: 12px;
            line-height: 1.5;
        }}
    </style>
</head>
<body>
    <div id="map"></div>
    <script type="text/javascript">
        var container = document.getElementById('map');
        var options = {{
            center: new kakao.maps.LatLng({center_lat}, {center_lng}),
            level: {zoom_level}
        }};
        
        var map = new kakao.maps.Map(container, options);
        var markers = {markers_json};
        
        markers.forEach(function(hospital) {{
            var markerPosition = new kakao.maps.LatLng(hospital.lat, hospital.lng);
            var marker = new kakao.maps.Marker({{
                position: markerPosition,
                title: hospital.name
            }});
            marker.setMap(map);
            
            var infoWindowContent = '<div class="info-window">' +
                '<div class="info-window-title">' + hospital.name + '</div>' +
                '<div class="info-window-content">' +
                '<p>주소: ' + hospital.address + '</p>' +
                '<p>전화: ' + hospital.phone + '</p>' +
                '<p>상태: ' + hospital.status + '</p>' +
                '</div></div>';
            
            var infoWindow = new kakao.maps.InfoWindow({{
                content: infoWindowContent
            }});
            
            kakao.maps.event.addListener(marker, 'click', function() {{
                infoWindow.open(map, marker);
            }});
        }});
    </script>
</body>
</html>
"""
        logger.debug(f"카카오맵 HTML 생성 완료: {len(markers)}개 병원")
        return html

