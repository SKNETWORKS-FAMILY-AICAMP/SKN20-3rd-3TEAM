"""
핸들러 기본 인터페이스
"""
from abc import ABC, abstractmethod
from typing import Dict, Any


class BaseHandler(ABC):
    """모든 핸들러의 기본 인터페이스"""
    
    @abstractmethod
    def handle(self, query: str, **kwargs) -> Dict[str, Any]:
        """
        질문을 처리
        
        Args:
            query: 사용자 질문
            **kwargs: 추가 파라미터
            
        Returns:
            처리 결과 딕셔너리
        """
        pass

