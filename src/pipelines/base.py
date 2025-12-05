"""
파이프라인 기본 인터페이스
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List


class BasePipeline(ABC):
    """모든 파이프라인의 기본 인터페이스"""
    
    @abstractmethod
    def process(self, query: str, **kwargs) -> Dict[str, Any]:
        """
        질문을 처리
        
        Args:
            query: 사용자 질문
            **kwargs: 추가 파라미터
            
        Returns:
            처리 결과 딕셔너리
        """
        pass
    
    @abstractmethod
    def batch_process(self, queries: List[str], **kwargs) -> List[Dict[str, Any]]:
        """
        여러 질문을 배치 처리
        
        Args:
            queries: 질문 리스트
            **kwargs: 추가 파라미터
            
        Returns:
            결과 리스트
        """
        pass

