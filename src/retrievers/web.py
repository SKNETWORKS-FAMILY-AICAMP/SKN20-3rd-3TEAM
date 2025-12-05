"""
웹 검색기
Tavily API를 사용한 웹 검색
"""
from typing import List, Dict, Any, Optional
from .base import BaseSearcher
from src.utils import get_logger
from src.config import get_settings

logger = get_logger(__name__)

# Tavily Search 동적 로드
_tavily_available = False
try:
    from langchain_community.tools.tavily_search import TavilySearchResults
    _tavily_available = True
except ImportError:
    logger.warning("TavilySearchResults를 로드할 수 없습니다")


class WebSearcher(BaseSearcher):
    """Tavily API를 사용한 웹 검색"""
    
    def __init__(self, api_key: Optional[str] = None, max_results: int = 3):
        """
        Args:
            api_key: Tavily API 키
            max_results: 반환할 최대 검색 결과 수
        """
        self.max_results = max_results
        self.api_key = api_key or get_settings().external_api.tavily_api_key
        self.search_tool = None
        
        if not self.api_key:
            logger.warning("Tavily API 키가 설정되지 않았습니다")
        elif _tavily_available:
            try:
                self.search_tool = TavilySearchResults(
                    max_results=max_results,
                    include_answer=True
                )
                logger.info("WebSearcher 초기화 완료")
            except Exception as e:
                logger.error(f"WebSearcher 초기화 실패: {str(e)}")
        else:
            logger.warning("Tavily 라이브러리를 사용할 수 없습니다")
    
    def search(self, query: str, **kwargs) -> List[Dict[str, Any]]:
        """
        웹에서 검색
        
        Args:
            query: 검색 쿼리
            **kwargs: 추가 파라미터
            
        Returns:
            검색 결과 리스트
        """
        if not self.search_tool:
            logger.warning("웹 검색 도구를 사용할 수 없습니다")
            return []
        
        logger.debug(f"웹 검색: query='{query}'")
        
        try:
            results = self.search_tool.invoke({"query": query})
            
            search_results = []
            if isinstance(results, list):
                for result in results:
                    if isinstance(result, dict):
                        search_results.append({
                            'content': result.get('content', result.get('snippet', '')),
                            'metadata': {
                                'title': result.get('title', ''),
                                'url': result.get('url', result.get('link', ''))
                            },
                            'relevance_score': 0.7,  # 웹 검색은 점수 미사용
                            'is_web_source': True,
                            'source': result.get('url', result.get('link', 'unknown')),
                            'title': result.get('title', '')
                        })
            
            logger.debug(f"웹 검색 완료: {len(search_results)}개 결과")
            return search_results
        
        except Exception as e:
            logger.error(f"웹 검색 중 오류: {str(e)}")
            return []

