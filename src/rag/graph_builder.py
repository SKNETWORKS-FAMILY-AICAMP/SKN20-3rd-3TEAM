"""
LangGraph 그래프 구성

CRAG 파이프라인의 워크플로우를 정의합니다.
"""

from typing import Any, Dict

from src.config.logger import get_logger
from src.rag.nodes.generation_node import generation_node
from src.rag.nodes.relevance_node import relevance_node
from src.rag.nodes.retrieval_node import retrieval_node
from src.rag.nodes.web_search_node import (
    convert_web_results_to_documents,
    web_search_node,
)

logger = get_logger(__name__)


def build_crag_graph() -> Dict[str, Any]:
    """
    CRAG (Corrective RAG) 파이프라인 그래프를 구성합니다.

    Returns:
        Dict: 그래프 구성 정보

    Note:
        LangGraph 구조:
        1. retrieval_node: 벡터 검색
        2. relevance_node: 관련성 판단
        3. 조건부 분기:
           - 관련 문서 있음 → generation_node
           - 관련 문서 없음 → web_search_node → generation_node
        4. generation_node: 최종 답변 생성

        향후 langgraph 라이브러리 통합 시 이를 활용:
        ```python
        from langgraph.graph import StateGraph

        graph = StateGraph(State)
        graph.add_node("retrieve", retrieval_node)
        graph.add_node("relevance", relevance_node)
        graph.add_node("web_search", web_search_node)
        graph.add_node("generate", generation_node)

        graph.set_entry_point("retrieve")
        graph.add_edge("retrieve", "relevance")
        graph.add_conditional_edges(
            "relevance",
            should_web_search,
            {"continue": "generate", "web_search": "web_search"}
        )
        graph.add_edge("web_search", "generate")
        graph.set_finish_point("generate")

        return graph.compile()
        ```
    """
    logger.info("Building CRAG graph")

    graph_config = {
        "nodes": [
            {
                "name": "retrieval",
                "function": retrieval_node,
                "description": "벡터 검색을 수행합니다",
            },
            {
                "name": "relevance",
                "function": relevance_node,
                "description": "검색된 문서의 관련성을 판단합니다",
            },
            {
                "name": "web_search",
                "function": web_search_node,
                "description": "관련 문서 없을 시 웹 검색을 수행합니다",
            },
            {
                "name": "generation",
                "function": generation_node,
                "description": "최종 답변을 생성합니다",
            },
        ],
        "edges": [
            {"from": "retrieval", "to": "relevance"},
            {
                "from": "relevance",
                "to": ["web_search", "generation"],
                "condition": "needs_web_search",
            },
            {"from": "web_search", "to": "generation"},
        ],
        "entry_point": "retrieval",
        "exit_point": "generation",
    }

    return graph_config


def should_web_search(state: Dict[str, Any]) -> str:
    """
    웹 검색 필요 여부를 판단하는 조건 함수

    Args:
        state: LangGraph 상태 딕셔너리

    Returns:
        str: "web_search" 또는 "generate"
    """
    needs_web_search = state.get("needs_web_search", False)
    return "web_search" if needs_web_search else "generate"


def execute_node(node_function, state: Dict[str, Any]) -> Dict[str, Any]:
    """
    개별 노드를 실행합니다.

    Args:
        node_function: 실행할 노드 함수
        state: 현재 상태

    Returns:
        Dict: 업데이트된 상태
    """
    logger.debug(f"Executing node: {node_function.__name__}")
    return node_function(state)


def run_crag_pipeline(query: str, intent: str = "medical") -> Dict[str, Any]:
    """
    CRAG 파이프라인을 순차적으로 실행합니다 (LangGraph 미사용 버전).

    Args:
        query: 검색 쿼리
        intent: 질문 의도

    Returns:
        Dict: 최종 결과 상태

    Note:
        이것은 임시 구현이며, 향후 langgraph 라이브러리로 대체됩니다.
        현재는 노드를 순차적으로 실행하는 방식입니다.
    """
    logger.info(f"Running CRAG pipeline for query: '{query}'")

    # 초기 상태 설정
    state = {
        "query": query,
        "intent": intent,
        "documents": [],
        "relevant_documents": [],
        "web_search_results": [],
        "answer": "",
        "retrieval_performed": False,
        "web_search_performed": False,
        "generation_performed": False,
    }

    try:
        # 1. 검색 노드
        logger.info("Step 1: Retrieval")
        state = execute_node(retrieval_node, state)

        # 2. 관련성 판단 노드
        logger.info("Step 2: Relevance evaluation")
        state = execute_node(relevance_node, state)

        # 3. 조건부 분기: 웹 검색 필요 여부
        if state.get("needs_web_search", False):
            logger.info("Step 3: Web search fallback")
            state = execute_node(web_search_node, state)

            # 웹 검색 결과를 Document 객체로 변환
            web_docs = convert_web_results_to_documents(
                state.get("web_search_results", [])
            )
            state["documents"].extend(web_docs)

        else:
            logger.info("Step 3: Skipped web search (relevant documents found)")

        # 4. 답변 생성 노드
        logger.info("Step 4: Answer generation")
        state = execute_node(generation_node, state)

        logger.info("CRAG pipeline completed successfully")
        return state

    except Exception as e:
        logger.error(f"CRAG pipeline error: {str(e)}")
        state["error"] = str(e)
        return state

