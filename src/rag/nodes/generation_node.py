"""
LangGraph 답변 생성 노드

검색된 문서를 기반으로 최종 답변을 생성하는 노드입니다.
"""

from typing import Any, Dict

from src.config.logger import get_logger

logger = get_logger(__name__)


def generation_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    문서 기반 답변 생성 노드

    Args:
        state: LangGraph 상태 딕셔너리
            - query: str (원본 질문)
            - documents: List[Document] (참고 문서)
            - web_search_results: List[Dict] (웹 검색 결과)
            - answer: str (생성된 답변)

    Returns:
        Dict: 업데이트된 상태

    Note:
        현재는 간단한 답변 생성 로직을 사용합니다.
        추후 LLM을 활용하여 더 정교한 답변 생성 가능
    """
    logger.info("Starting generation node")

    query = state.get("query", "")
    documents = state.get("documents", [])
    web_results = state.get("web_search_results", [])

    try:
        # 답변 생성
        answer = _generate_answer(query, documents, web_results)

        state["answer"] = answer
        state["generation_performed"] = True

        logger.info("Answer generated successfully")
        return state

    except Exception as e:
        logger.error(f"Generation node error: {str(e)}")
        state["answer"] = "답변 생성 중 오류가 발생했습니다."
        state["generation_error"] = str(e)
        return state


def _generate_answer(
    query: str, documents: list, web_results: list
) -> str:
    """
    문서를 기반으로 답변을 생성합니다 (현재 기본 구현).

    Args:
        query: 사용자 질문
        documents: 벡터 검색 결과 문서
        web_results: 웹 검색 결과

    Returns:
        str: 생성된 답변

    Note:
        이 함수는 기본 구현이며, 다음과 같이 확장 가능:
        1. LLM (OpenAI, Claude 등) 활용
        2. Prompt Engineering
        3. Few-shot learning
        4. RAG 최적화 기법 적용
    """
    # 기본 구현: 문서의 내용을 조합하여 답변 생성
    if documents:
        # 상위 점수의 문서 선택
        top_doc = max(documents, key=lambda d: d.score or 0.0)
        answer = f"질문: {query}\n\n참고 정보:\n{top_doc.content}"

        if len(documents) > 1:
            answer += "\n\n추가 정보:\n"
            for doc in documents[1:]:
                answer += f"- {doc.content[:100]}...\n"

        return answer

    elif web_results:
        # 웹 검색 결과가 있는 경우
        answer = f"질문: {query}\n\n웹 검색 결과:\n"
        for result in web_results[:3]:
            answer += f"- {result.get('snippet', result.get('content', ''))}\n"
            answer += f"  출처: {result.get('source', 'Unknown')}\n"

        return answer

    else:
        # 문서가 없는 경우
        return (
            f"죄송하지만, '{query}'에 대한 정보를 찾을 수 없습니다. "
            "동물병원 전문가에게 상담을 받으시기를 권장합니다."
        )


def generation_node_llm(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    LLM 기반 답변 생성 노드 (placeholder)

    Args:
        state: LangGraph 상태 딕셔너리

    Returns:
        Dict: 업데이트된 상태

    Note:
        이 함수는 향후 LLM을 사용하여 더 정교한 답변 생성을 수행합니다.
        구현 시 다음을 수행할 수 있습니다:
        1. OpenAI GPT-4 또는 Claude 호출
        2. 문서를 context로 사용하는 프롬프트 작성
        3. 체인 오브 쏘트(Chain of Thought) 구현
        4. 응답 평가 및 피드백 루프

        구현 예시:
        ```python
        from langchain.llms import ChatOpenAI
        from langchain.prompts import ChatPromptTemplate

        llm = ChatOpenAI(model="gpt-4")

        prompt = ChatPromptTemplate.from_template(
            "질문: {query}\n\n문서: {context}\n\n답변:"
        )

        context = "\n".join([doc.content for doc in documents])
        response = llm.invoke(prompt.format(query=query, context=context))
        ```
    """
    logger.info("LLM-based answer generation (not implemented yet)")

    # TODO: LLM 기반 답변 생성 구현
    # from langchain.llms import ChatOpenAI
    # from langchain.prompts import ChatPromptTemplate
    #
    # llm = ChatOpenAI(model="gpt-4", temperature=0.7)
    # prompt = ChatPromptTemplate.from_template(...)
    # chain = prompt | llm
    # response = chain.invoke({"query": query, ...})

    return state

