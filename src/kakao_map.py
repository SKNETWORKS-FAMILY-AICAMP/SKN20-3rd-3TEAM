"""
카카오맵 통합 모듈
병원 정보를 CSV/웹에서 가져와 카카오맵으로 시각화
"""

import os
import json
import pandas as pd
from typing import Dict, List, Optional, Tuple
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()

KAKAO_API_KEY = os.getenv("KAKAO_API_KEY")


class HospitalMapper:
    """병원 정보를 카카오맵에 표시하는 클래스"""
    
    def __init__(self, kakao_api_key: Optional[str] = None):
        """
        초기화
        
        Args:
            kakao_api_key: 카카오맵 REST API 키
        """
        self.kakao_api_key = kakao_api_key or KAKAO_API_KEY
        if not self.kakao_api_key:
            raise ValueError("KAKAO_API_KEY not found in environment variables")
    
    
    def load_hospitals_from_csv(self, csv_path: str) -> List[Dict]:
        """
        CSV 파일에서 병원 정보 로드
        
        Args:
            csv_path: CSV 파일 경로 (JSON 형식인 경우도 처리)
            
        Returns:
            병원 정보 리스트
        """
        hospitals = []
        
        if csv_path.endswith('.json'):
            # JSON 파일 처리
            with open(csv_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if 'DATA' in data:
                    hospitals = data['DATA']
        else:
            # CSV 파일 처리
            df = pd.read_csv(csv_path, encoding='utf-8')
            hospitals = df.to_dict('records')
        
        # 필터링: 도로명주소가 있는 영업 중인 병원만
        filtered_hospitals = [
            h for h in hospitals
            if h.get('rdnwhladdr') and h.get('trdstategbn') == '01'
        ]
        
        return filtered_hospitals
    
    
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
            'address': hospital.get('rdnwhladdr', ''),
            'phone': hospital.get('sitetel', ''),
            'lat': float(hospital.get('y', 0)) if hospital.get('y') else None,
            'lng': float(hospital.get('x', 0)) if hospital.get('x') else None,
            'status': '영업 중' if hospital.get('trdstategbn') == '01' else '폐업',
        }
    
    
    def create_kakao_map_html(self, hospitals: List[Dict], center_lat: float = 37.5665,
                             center_lng: float = 126.9780, zoom_level: int = 5) -> str:
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
        # 마커 데이터 생성
        markers = []
        for i, hospital in enumerate(hospitals):
            if hospital.get('lat') and hospital.get('lng'):
                marker = {
                    'title': hospital['name'],
                    'latlng': [hospital['lat'], hospital['lng']],
                    'address': hospital['address'],
                    'phone': hospital['phone'],
                }
                markers.append(marker)
        
        # 마커 데이터를 JSON으로 변환
        markers_json = json.dumps(markers, ensure_ascii=False)
        
        # HTML 생성
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>카카오맵 병원 위치</title>
            <script src="https://dapi.kakao.com/v2/maps/sdk.js?appkey={self.kakao_api_key}&libraries=services"></script>
            <style>
                body {{
                    margin: 0;
                    padding: 0;
                    font-family: Arial, sans-serif;
                }}
                #map {{
                    width: 100%;
                    height: 600px;
                }}
                .info-window {{
                    padding: 12px;
                    background-color: white;
                    border-radius: 8px;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.2);
                }}
                .info-window h4 {{
                    margin: 0 0 8px 0;
                    color: #333;
                    font-size: 14px;
                }}
                .info-window p {{
                    margin: 4px 0;
                    color: #666;
                    font-size: 12px;
                }}
                .hospital-list {{
                    background-color: #f5f5f5;
                    padding: 20px;
                    border-radius: 8px;
                    margin-top: 20px;
                }}
                .hospital-item {{
                    background-color: white;
                    padding: 12px;
                    margin: 8px 0;
                    border-radius: 4px;
                    border-left: 4px solid #FF6B6B;
                }}
                .hospital-item h5 {{
                    margin: 0 0 6px 0;
                    color: #333;
                }}
                .hospital-item p {{
                    margin: 2px 0;
                    color: #666;
                    font-size: 12px;
                }}
            </style>
        </head>
        <body>
            <div id="map"></div>
            
            <div class="hospital-list">
                <h3>🏥 등록된 병원 목록 ({len(markers)}개)</h3>
                <div id="hospitalList"></div>
            </div>
            
            <script>
                // 지도 초기화
                const mapContainer = document.getElementById('map');
                const mapOption = {{
                    center: new kakao.maps.LatLng({center_lat}, {center_lng}),
                    level: {zoom_level}
                }};
                
                const map = new kakao.maps.Map(mapContainer, mapOption);
                
                // 마커 데이터
                const markersData = {markers_json};
                
                // 마커 및 정보창 생성
                const infoWindows = [];
                
                markersData.forEach((data, index) => {{
                    const markerPosition = new kakao.maps.LatLng(data.latlng[0], data.latlng[1]);
                    
                    const marker = new kakao.maps.Marker({{
                        position: markerPosition,
                        title: data.title,
                        image: createMarkerImage(index)
                    }});
                    
                    marker.setMap(map);
                    
                    // 정보창 HTML
                    const infoWindowContent = `
                        <div class="info-window">
                            <h4>🏥 ${{data.title}}</h4>
                            <p><strong>📍 주소:</strong> ${{data.address}}</p>
                            <p><strong>📞 전화:</strong> ${{data.phone || '정보 없음'}}</p>
                        </div>
                    `;
                    
                    const infoWindow = new kakao.maps.InfoWindow({{
                        content: infoWindowContent,
                        removable: false
                    }});
                    
                    infoWindows.push(infoWindow);
                    
                    // 마커 클릭 이벤트
                    kakao.maps.event.addListener(marker, 'click', function() {{
                        // 기존 정보창 닫기
                        infoWindows.forEach(iw => iw.close());
                        // 새 정보창 열기
                        infoWindow.open(map, marker);
                    }});
                }});
                
                // 마커 이미지 생성
                function createMarkerImage(index) {{
                    const imageSrc = 'https://t1.daumcdn.net/localimg/localimages/07/mapapidoc/marker_red.png';
                    const imageSize = new kakao.maps.Size(33, 36);
                    const imageOption = {{offset: new kakao.maps.Point(16, 36)}};
                    return new kakao.maps.MarkerImage(imageSrc, imageSize, imageOption);
                }}
                
                // 병원 목록 표시
                const hospitalList = document.getElementById('hospitalList');
                markersData.forEach((data, index) => {{
                    const item = document.createElement('div');
                    item.className = 'hospital-item';
                    item.innerHTML = `
                        <h5>(${{index + 1}}) ${{data.title}}</h5>
                        <p><strong>📍</strong> ${{data.address}}</p>
                        <p><strong>📞</strong> ${{data.phone || '정보 없음'}}</p>
                    `;
                    hospitalList.appendChild(item);
                }});
            </script>
        </body>
        </html>
        """
        
        return html
    
    
    def create_streamlit_html_component(self, hospitals: List[Dict], height: int = 700) -> str:
        """
        Streamlit용 HTML 컴포넌트 생성
        
        Args:
            hospitals: 병원 정보 리스트
            height: 지도 높이
            
        Returns:
            Streamlit용 HTML 코드
        """
        if not hospitals:
            return "<p style='color: red;'>표시할 병원 정보가 없습니다.</p>"
        
        # 마커 데이터 생성
        markers = []
        for i, hospital in enumerate(hospitals):
            if hospital.get('lat') and hospital.get('lng'):
                marker = {
                    'title': hospital['name'],
                    'latlng': [hospital['lat'], hospital['lng']],
                    'address': hospital['address'],
                    'phone': hospital['phone'],
                }
                markers.append(marker)
        
        if not markers:
            return "<p style='color: red;'>좌표 정보가 있는 병원이 없습니다.</p>"
        
        markers_json = json.dumps(markers, ensure_ascii=False)
        
        html = f"""
        <div style="width: 100%; height: {height}px; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
            <div id="kakao-map" style="width: 100%; height: 100%;"></div>
        </div>
        
        <script src="https://dapi.kakao.com/v2/maps/sdk.js?appkey={self.kakao_api_key}&libraries=services"></script>
        <script>
            // 카카오맵 API 로드 완료 대기
            function initializeMap() {{
                if (typeof kakao === 'undefined') {{
                    // API 로드 대기
                    setTimeout(initializeMap, 100);
                    return;
                }}
                
                const mapContainer = document.getElementById('kakao-map');
                if (!mapContainer) return;
                
                const mapOption = {{
                    center: new kakao.maps.LatLng(37.5665, 126.9780),
                    level: 6
                }};
                
                const map = new kakao.maps.Map(mapContainer, mapOption);
            
                const markersData = {markers_json};
                const infoWindows = [];
                
                markersData.forEach((data, index) => {{
                    const markerPosition = new kakao.maps.LatLng(data.latlng[0], data.latlng[1]);
                    
                    const marker = new kakao.maps.Marker({{
                        position: markerPosition,
                        title: data.title
                    }});
                    
                    marker.setMap(map);
                    
                    const infoWindowContent = `
                        <div style="padding: 12px; background-color: white; border-radius: 4px; min-width: 200px;">
                            <h4 style="margin: 0 0 8px 0; color: #333;">🏥 ${{data.title}}</h4>
                            <p style="margin: 4px 0; color: #666; font-size: 12px;"><strong>📍</strong> ${{data.address}}</p>
                            <p style="margin: 4px 0; color: #666; font-size: 12px;"><strong>📞</strong> ${{data.phone || '정보 없음'}}</p>
                        </div>
                    `;
                    
                    const infoWindow = new kakao.maps.InfoWindow({{
                        content: infoWindowContent,
                        removable: false
                    }});
                    
                    infoWindows.push(infoWindow);
                    
                    kakao.maps.event.addListener(marker, 'click', function() {{
                        infoWindows.forEach(iw => iw.close());
                        infoWindow.open(map, marker);
                    }});
                }});
                
                // 모든 마커가 보이도록 지도 범위 조정
                if (markersData.length > 0) {{
                    const bounds = new kakao.maps.LatLngBounds();
                    markersData.forEach(data => {{
                        bounds.extend(new kakao.maps.LatLng(data.latlng[0], data.latlng[1]));
                    }});
                    map.setBounds(bounds);
                }}
            }}
            
            // 페이지 로드 후 맵 초기화
            if (document.readyState === 'loading') {{
                document.addEventListener('DOMContentLoaded', initializeMap);
            }} else {{
                initializeMap();
            }}
        </script>
        """
        
        return html

