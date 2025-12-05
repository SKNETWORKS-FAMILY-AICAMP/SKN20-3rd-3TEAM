"""
웹검색 클라이언트 - Tavily API
"""
from typing import List, Dict
from tavily import TavilyClient
from app.config import settings


class WebSearchClient:
    """Tavily를 사용한 웹검색 클라이언트"""
    
    def __init__(self):
        if settings.TAVILY_API_KEY:
            self.client = TavilyClient(api_key=settings.TAVILY_API_KEY)
            self.enabled = True
        else:
            self.client = None
            self.enabled = False
            print("⚠️ Tavily API 키가 없습니다. 웹검색이 비활성화됩니다.")
    
    def search(self, query: str, max_results: int = 3, timeout: int = 10) -> List[Dict[str, str]]:
        """
        웹에서 정보 검색
        
        Args:
            query: 검색 쿼리
            max_results: 최대 결과 수
            timeout: 타임아웃 (초)
            
        Returns:
            List[Dict]: 검색 결과 리스트
        """
        if not self.enabled:
            return []
        
        try:
            import signal
            
            # 타임아웃 설정
            def timeout_handler(signum, frame):
                raise TimeoutError("웹검색 시간 초과")
            
            # Windows에서는 signal.alarm이 없으므로 다른 방법 사용
            from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError
            
            def do_search():
                return self.client.search(
                    query=query,
                    search_depth="basic",
                    max_results=max_results,
                    include_answer=True,
                    include_raw_content=False
                )
            
            # 타임아웃을 적용한 검색 실행
            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(do_search)
                try:
                    response = future.result(timeout=timeout)
                except FuturesTimeoutError:
                    print(f"⚠️ 웹검색 타임아웃 ({timeout}초 초과)")
                    return []
            
            results = []
            
            # 검색 결과 파싱
            for item in response.get('results', []):
                results.append({
                    'title': item.get('title', ''),
                    'content': item.get('content', ''),
                    'url': item.get('url', ''),
                    'score': item.get('score', 0.0)
                })
            
            # Tavily의 AI 요약이 있으면 추가
            if response.get('answer'):
                results.insert(0, {
                    'title': 'AI 요약',
                    'content': response['answer'],
                    'url': '',
                    'score': 1.0
                })
            
            return results
            
        except Exception as e:
            print(f"웹검색 실패: {e}")
            return []
    
    def search_korean(self, query: str, max_results: int = 3) -> List[Dict[str, str]]:
        """
        한국어 특화 검색 (강아지 + 질문 키워드 조합)
        
        Args:
            query: 검색 쿼리
            max_results: 최대 결과 수
            
        Returns:
            List[Dict]: 검색 결과 리스트
        """
        # 강아지 관련 키워드 추가
        enhanced_query = f"강아지 {query} 수의사 조언"
        return self.search(enhanced_query, max_results)


# 싱글톤 인스턴스
web_search_client = WebSearchClient()