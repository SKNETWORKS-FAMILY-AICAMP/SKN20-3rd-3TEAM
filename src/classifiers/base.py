"""
분류기 기본 인터페이스
"""
from abc import ABC, abstractmethod
from typing import Tuple, Any


class BaseClassifier(ABC):
    """모든 분류기의 기본 인터페이스"""
    
    @abstractmethod
    def classify(self, text: str) -> Tuple[Any, float, str]:
        """
        텍스트를 분류
        
        Args:
            text: 분류할 텍스트
            
        Returns:
            (분류 결과, 신뢰도, 분류 사유) 튜플
        """
        pass

