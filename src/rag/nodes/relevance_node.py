"""
LangGraph 관련성 판단 노드

검색된 문서의 관련성을 평가하는 노드입니다.
"""

from typing import Any, Dict

from src.config.logger import get_logger
from src.config.settings import settings

logger = get_logger(__name__)


def relevance_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    검색된 문서의 관련성을 판단하는 노드

    Args:
        state: LangGraph 상태 딕셔너리
            - documents: List[Document] (검색 결과)
            - relevant_documents: List[Document] (관련성 높은 문서)
            - needs_web_search: bool (웹 검색 필요 여부)

    Returns:
        Dict: 업데이트된 상태

    Note:
        CRAG(Corrective RAG) 패러다임의 핵심:
        - 검색된 문서의 관련성을 평가
        - 관련성 낮으면 웹 검색으로 폴백
        - 현재는 간단한 threshold 기반이나, 추후 LLM 기반으로 확장 가능
    """
    logger.info("Starting relevance node")

    documents = state.get("documents", [])
    threshold = settings.RELEVANCE_THRESHOLD

    if not documents:
        logger.warning("No documents to evaluate for relevance")
        state["relevant_documents"] = []
        state["needs_web_search"] = True
        return state

    try:
        # 관련성 평가
        relevant_docs = []
        for doc in documents:
            score = doc.score if doc.score is not None else 0.0

            if score >= threshold:
                relevant_docs.append(doc)
                logger.debug(
                    f"Document '{doc.id}' is relevant (score: {score:.2f})"
                )
            else:
                logger.debug(
                    f"Document '{doc.id}' is not relevant (score: {score:.2f})"
                )

        # 관련 문서가 없으면 웹 검색 필요
        needs_web_search = len(relevant_docs) == 0
        if needs_web_search:
            logger.info(
                "No relevant documents found. Web search fallback triggered."
            )

        state["relevant_documents"] = relevant_docs
        state["needs_web_search"] = needs_web_search

        return state

    except Exception as e:
        logger.error(f"Relevance evaluation error: {str(e)}")
        state["relevant_documents"] = []
        state["needs_web_search"] = True
        return state


def relevance_node_llm(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    LLM 기반 관련성 판단 노드 (placeholder)

    Args:
        state: LangGraph 상태 딕셔너리

    Returns:
        Dict: 업데이트된 상태

    Note:
        이 함수는 향후 LLM을 사용하여 더 정교한 관련성 판단을 수행합니다.
        구현 시 다음을 수행할 수 있습니다:
        1. 각 문서와 쿼리 간의 의미적 관련성 평가
        2. 문서가 질문에 직접적으로 답하는지 판단
        3. 신뢰성 점수 추가 계산
    """
    logger.info("LLM-based relevance evaluation (not implemented yet)")

    # TODO: LLM 기반 관련성 판단 구현
    # 예시:
    # prompt = f"다음 문서가 질문에 답하는가? 점수 0-1\n문서: {doc.content}\n질문: {state['query']}"
    # response = llm.invoke(prompt)

    return state

