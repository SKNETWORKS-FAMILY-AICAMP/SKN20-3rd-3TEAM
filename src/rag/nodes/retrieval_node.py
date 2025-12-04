"""
LangGraph 검색 노드

문서 검색을 수행하는 노드입니다.
"""

from typing import Any, Dict

from src.config.logger import get_logger
from src.retriever.vector_store_retriever import VectorStoreRetriever

logger = get_logger(__name__)


def retrieval_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    벡터 검색을 수행하는 노드

    Args:
        state: LangGraph 상태 딕셔너리
            - query: str (검색 쿼리)
            - documents: List[Document] (검색 결과)
            - intent: str (질문 의도)

    Returns:
        Dict: 업데이트된 상태

    Note:
        이 노드는 CRAG 파이프라인의 첫 번째 단계입니다.
        벡터 검색을 통해 관련 문서를 찾습니다.
    """
    logger.info("Starting retrieval node")

    query = state.get("query", "")
    
    if not query:
        logger.warning("No query provided to retrieval node")
        return {"documents": [], "retrieval_performed": True}

    try:
        # 벡터 검색 수행
        retriever = VectorStoreRetriever()
        result = retriever.search(query, top_k=5)

        documents = result.documents

        logger.info(f"Retrieved {len(documents)} documents")

        # 상태 업데이트
        state["documents"] = documents
        state["retrieval_performed"] = True

        return state

    except Exception as e:
        logger.error(f"Retrieval node error: {str(e)}")
        state["documents"] = []
        state["retrieval_performed"] = False
        state["retrieval_error"] = str(e)
        return state

