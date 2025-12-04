"""
웹 검색을 통한 병원 정보 조회 모듈
"""

import re
from typing import Dict, Optional, List
from langchain_community.tools.tavily_search import TavilySearchResults
import logging

logger = logging.getLogger(__name__)


class HospitalWebSearcher:
    """웹 검색을 통해 병원 정보를 조회하는 클래스"""
    
    def __init__(self):
        """초기화"""
        try:
            self.search_tool = TavilySearchResults(max_results=5)
        except Exception as e:
            logger.warning(f"TavilySearchResults initialization warning: {str(e)}")
            self.search_tool = None
    
    
    def search_hospital_address(self, hospital_name: str, location: str = "서울") -> Optional[str]:
        """
        병원 이름과 지역을 통해 웹에서 도로명 주소 검색
        
        Args:
            hospital_name: 병원 이름
            location: 지역 (기본값: 서울)
            
        Returns:
            도로명 주소 또는 None
        """
        if not self.search_tool:
            logger.warning("TavilySearchResults not available")
            return None
        
        try:
            # 검색 쿼리
            query = f"{hospital_name} 동물병원 도로명주소 {location}"
            
            # 웹 검색
            results = self.search_tool.run(query)
            
            if not results:
                logger.info(f"No search results for: {query}")
                return None
            
            # 첫 번째 결과에서 주소 추출 시도
            address = self._extract_address_from_search_results(results, hospital_name)
            
            return address
        
        except Exception as e:
            logger.error(f"Hospital web search error: {str(e)}")
            return None
    
    
    def _extract_address_from_search_results(self, results: str, hospital_name: str) -> Optional[str]:
        """
        검색 결과에서 주소 추출
        
        Args:
            results: 검색 결과 텍스트
            hospital_name: 병원 이름
            
        Returns:
            주소 또는 None
        """
        # 도로명주소 패턴 (선택사항)
        patterns = [
            r"서울[시|특별시][^\s]*\s*[\w구|동|로|길]+\s+[\d-]+",  # 서울 도로명 주소
            r"[\w구|동]+\s*[\d]+(?:번지|\-)?(?:[\s\w]+)*",  # 기본 주소 패턴
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, results)
            if matches:
                # 가장 긴 주소 반환 (더 상세할 가능성)
                longest = max(matches, key=len)
                return longest.strip()
        
        # 패턴 매칭 실패 시 첫 번째 줄 반환
        lines = results.split('\n')
        if lines and len(lines[0]) > 5:
            return lines[0].strip()
        
        return None
    
    
    def search_hospital_info(self, hospital_name: str, location: str = "서울") -> Dict:
        """
        병원 정보 전체 검색
        
        Args:
            hospital_name: 병원 이름
            location: 지역
            
        Returns:
            병원 정보 딕셔너리
        """
        info = {
            'name': hospital_name,
            'location': location,
            'address': None,
            'phone': None,
            'source': 'web',
            'found': False
        }
        
        # 주소 검색
        address = self.search_hospital_address(hospital_name, location)
        if address:
            info['address'] = address
            info['found'] = True
        
        return info


def extract_hospital_name_from_question(question: str) -> Optional[str]:
    """
    질문에서 병원 이름 추출
    
    Args:
        question: 질문 텍스트
        
    Returns:
        병원 이름 또는 None
        
    Examples:
        >>> extract_hospital_name_from_question("강아지 피부질환으로 서울에 있는 ABC동물병원에 가고 싶어")
        "ABC동물병원"
    """
    # 동물병원 패턴 찾기
    pattern = r"(\w+)\s*동물(?:병원|의료센터|메디컬센터)"
    
    match = re.search(pattern, question)
    if match:
        return match.group(1) + "동물병원"
    
    return None


def extract_location_from_question(question: str) -> str:
    """
    질문에서 지역 정보 추출
    
    Args:
        question: 질문 텍스트
        
    Returns:
        지역명 (기본값: "서울")
        
    Examples:
        >>> extract_location_from_question("부산에 있는 좋은 동물병원이 어디일까?")
        "부산"
    """
    locations = ["서울", "부산", "대구", "인천", "광주", "대전", "울산", 
                "경기", "강원", "충북", "충남", "전북", "전남", "경북", "경남", "제주"]
    
    for loc in locations:
        if loc in question:
            return loc
    
    return "서울"  # 기본값

