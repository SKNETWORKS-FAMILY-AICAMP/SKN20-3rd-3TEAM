"""
LangGraph 웹 검색 노드

관련 문서가 없을 때 웹 검색으로 폴백하는 노드입니다.
"""

from typing import Any, Dict

from src.config.logger import get_logger
from src.web.general_web_searcher import GeneralWebSearcher
from src.web.hospital_web_searcher import HospitalWebSearcher

logger = get_logger(__name__)


def web_search_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    웹 검색을 수행하는 노드 (Fallback)

    Args:
        state: LangGraph 상태 딕셔너리
            - query: str (검색 쿼리)
            - intent: str (질문 의도)
            - web_search_results: List[Dict] (검색 결과)

    Returns:
        Dict: 업데이트된 상태

    Note:
        CRAG의 폴백 메커니즘:
        - 벡터 검색이 실패하거나 관련 문서가 없으면 웹 검색 수행
        - 의도에 따라 다른 검색기 사용
        - 검색 결과를 documents 형태로 변환하여 생성 노드에 전달
    """
    logger.info("Starting web search node")

    query = state.get("query", "")
    intent = state.get("intent", "general")

    if not query:
        logger.warning("No query provided to web search node")
        return {"web_search_results": [], "web_search_performed": False}

    try:
        # 의도에 따라 다른 검색기 사용
        if intent == "hospital":
            logger.info("Using HospitalWebSearcher for hospital query")
            searcher = HospitalWebSearcher()
            results = searcher.search(query)
        else:
            logger.info("Using GeneralWebSearcher for general query")
            searcher = GeneralWebSearcher()
            results = searcher.search(query)

        logger.info(f"Web search returned {len(results)} results")

        # 웹 검색 결과를 Document 형태로 변환하기 위한 데이터 저장
        state["web_search_results"] = results
        state["web_search_performed"] = True

        return state

    except Exception as e:
        logger.error(f"Web search node error: {str(e)}")
        state["web_search_results"] = []
        state["web_search_performed"] = False
        state["web_search_error"] = str(e)
        return state


def convert_web_results_to_documents(results: list[dict]) -> list:
    """
    웹 검색 결과를 Document 객체로 변환합니다.

    Args:
        results: 웹 검색 결과 리스트

    Returns:
        list: Document 객체 리스트

    Note:
        이 함수는 웹 검색 결과를 표준화된 Document 형식으로 변환합니다.
        반환된 문서는 생성 노드에서 사용됩니다.
    """
    from src.types.document import Document

    documents = []
    for result in results:
        doc = Document(
            id=result.get("link", result.get("url", "unknown")),
            content=result.get("snippet", result.get("content", "")),
            metadata={
                "title": result.get("title", ""),
                "source": result.get("source", "web"),
                "link": result.get("link", result.get("url", "")),
            },
            score=0.8,  # 웹 검색 결과는 기본 점수 설정
            source="web_search",
        )
        documents.append(doc)

    return documents

