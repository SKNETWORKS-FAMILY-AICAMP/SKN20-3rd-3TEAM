"""
검색기 기본 인터페이스
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any


class BaseSearcher(ABC):
    """모든 검색기의 기본 인터페이스"""
    
    @abstractmethod
    def search(self, query: str, **kwargs) -> List[Dict[str, Any]]:
        """
        검색 수행
        
        Args:
            query: 검색 쿼리
            **kwargs: 추가 파라미터
            
        Returns:
            검색 결과 리스트 (각 결과는 문서 정보를 담은 딕셔너리)
        """
        pass

