"""
내부 문서 검색기
Chroma 벡터스토어를 사용한 검색
"""
from typing import List, Dict, Any, Optional
from langchain_chroma import Chroma
from .base import BaseSearcher
from src.utils import get_logger

logger = get_logger(__name__)


class InternalSearcher(BaseSearcher):
    """벡터스토어를 사용한 내부 문서 검색"""
    
    def __init__(self, vectorstore: Chroma, top_k: int = 5):
        """
        Args:
            vectorstore: Chroma 벡터스토어
            top_k: 반환할 상위 문서 수
        """
        self.vectorstore = vectorstore
        self.top_k = top_k
        logger.info(f"InternalSearcher 초기화: top_k={top_k}")
    
    def search(
        self,
        query: str,
        top_k: Optional[int] = None,
        score_threshold: Optional[float] = None,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        내부 벡터스토어에서 검색
        
        Args:
            query: 검색 쿼리
            top_k: 반환할 상위 문서 수 (기본값: self.top_k)
            score_threshold: 최소 점수 기준 (기본값: 0.0)
            **kwargs: 추가 파라미터
            
        Returns:
            검색 결과 리스트
        """
        if top_k is None:
            top_k = self.top_k
        
        if score_threshold is None:
            score_threshold = 0.0
        
        logger.debug(f"내부 검색: query='{query}', top_k={top_k}")
        
        try:
            # 벡터스토어에서 검색
            results = self.vectorstore.similarity_search_with_score(query, k=top_k)
            
            search_results = []
            for doc, distance in results:
                # similarity score 계산
                similarity_score = 1.0 - distance if distance <= 1.0 else max(0.0, 1.0 - distance)
                
                # 기준점 이상인 문서만 반환
                if similarity_score >= score_threshold:
                    search_results.append({
                        'content': doc.page_content,
                        'metadata': doc.metadata,
                        'relevance_score': similarity_score,
                        'is_web_source': False,
                        'source': doc.metadata.get('file_name', 'unknown')
                    })
            
            logger.debug(f"내부 검색 완료: {len(search_results)}개 문서")
            return search_results
        
        except Exception as e:
            logger.error(f"내부 검색 중 오류: {str(e)}")
            return []

