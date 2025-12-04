"""
LangGraph 기반 CRAG 파이프라인

문서 검색, 관련성 판단, 웹 검색 폴백, 답변 생성을 통합합니다.
"""

from typing import Any, Dict, Optional

from src.config.logger import get_logger
from src.rag.graph_builder import run_crag_pipeline
from src.types.response import RAGResponse

logger = get_logger(__name__)


class LangGraphRAGPipeline:
    """
    LangGraph 기반 CRAG (Corrective RAG) 파이프라인

    벡터 검색 → 관련성 판단 → 웹 검색(필요시) → 답변 생성

    주요 특징:
    1. 벡터 검색으로 관련 문서 검색
    2. 관련성 임계값 확인
    3. 관련 문서 없으면 웹 검색으로 폴백
    4. 최종 답변 생성

    Note:
        현재는 순차 실행 방식이며, 향후 langgraph 라이브러리로 완전 마이그레이션:
        1. StateGraph 사용
        2. 조건부 엣지로 유연한 워크플로우
        3. 병렬 실행 지원
        4. 순환 로직 지원
    """

    def __init__(
        self,
        max_retries: int = 3,
        timeout: float = 30.0,
        debug: bool = False,
    ):
        """
        파이프라인 초기화

        Args:
            max_retries: 최대 재시도 횟수
            timeout: 타임아웃 (초)
            debug: 디버그 모드
        """
        self.max_retries = max_retries
        self.timeout = timeout
        self.debug = debug

        logger.info(
            f"LangGraphRAGPipeline initialized "
            f"(retries={max_retries}, timeout={timeout}s)"
        )

    def invoke(
        self, query: str, intent: str = "medical"
    ) -> RAGResponse:
        """
        파이프라인을 실행합니다.

        Args:
            query: 사용자 질문
            intent: 질문 의도 ("medical", "hospital", "general", "unknown")

        Returns:
            RAGResponse: 최종 응답

        Note:
            이 메서드는 전체 CRAG 워크플로우를 조정합니다:
            1. 입력 검증
            2. 파이프라인 실행
            3. 결과 정규화
            4. 응답 생성
        """
        import time

        logger.info(f"Invoking RAG pipeline for: '{query}'")
        start_time = time.time()

        try:
            # 입력 검증
            if not query or not query.strip():
                logger.warning("Empty query provided")
                return RAGResponse(
                    query=query,
                    answer="질문이 비어있습니다.",
                    documents=[],
                    intent=intent,
                )

            # 파이프라인 실행
            state = run_crag_pipeline(query, intent)

            # 결과 추출
            answer = state.get("answer", "답변을 생성할 수 없습니다.")
            documents = state.get("documents", [])
            web_search_performed = state.get("web_search_performed", False)

            # 응답 생성
            elapsed = time.time() - start_time

            response = RAGResponse(
                query=query,
                answer=answer,
                documents=documents,
                intent=intent,
                metadata={
                    "web_search_used": web_search_performed,
                    "document_count": len(documents),
                    "retrieval_success": state.get("retrieval_performed", False),
                },
                model="langgraph-crag",
                execution_time=elapsed,
            )

            logger.info(
                f"RAG pipeline completed successfully in {elapsed:.2f}s"
            )
            return response

        except Exception as e:
            logger.error(f"RAG pipeline error: {str(e)}")
            elapsed = time.time() - start_time

            return RAGResponse(
                query=query,
                answer=f"답변 생성 중 오류가 발생했습니다: {str(e)}",
                documents=[],
                intent=intent,
                metadata={"error": str(e)},
                execution_time=elapsed,
            )

    def invoke_batch(
        self, queries: list[str], intent: str = "medical"
    ) -> list[RAGResponse]:
        """
        여러 쿼리를 배치로 처리합니다.

        Args:
            queries: 질문 리스트
            intent: 질문 의도

        Returns:
            list[RAGResponse]: 응답 리스트
        """
        logger.info(f"Batch processing {len(queries)} queries")

        responses = [self.invoke(query, intent) for query in queries]

        logger.info(f"Batch processing completed: {len(responses)} responses")
        return responses

    def get_graph_config(self) -> Dict[str, Any]:
        """
        파이프라인의 그래프 구성을 반환합니다.

        Returns:
            Dict: 그래프 구성 정보

        Note:
            이 메서드는 파이프라인의 구조를 시각화하거나 디버깅할 때 유용합니다.
        """
        from src.rag.graph_builder import build_crag_graph

        return build_crag_graph()

    def add_custom_node(
        self,
        name: str,
        function: callable,
        input_key: str,
        output_key: str,
    ) -> None:
        """
        파이프라인에 커스텀 노드를 추가합니다.

        Args:
            name: 노드 이름
            function: 노드 함수
            input_key: 입력 상태 키
            output_key: 출력 상태 키

        Note:
            이 메서드는 향후 파이프라인 확장을 위한 인터페이스입니다.
            예시:
            ```python
            def custom_filter(state):
                # 커스텀 필터링 로직
                return state

            pipeline.add_custom_node(
                "filter",
                custom_filter,
                input_key="documents",
                output_key="filtered_documents"
            )
            ```
        """
        logger.info(f"Adding custom node: {name}")

        # TODO: 실제 커스텀 노드 추가 로직 구현
        # 현재는 placeholder
        pass

    def run_with_streaming(
        self, query: str, intent: str = "medical"
    ) -> Any:
        """
        스트리밍 방식으로 파이프라인을 실행합니다.

        Args:
            query: 사용자 질문
            intent: 질문 의도

        Yields:
            str: 스트리밍 결과

        Note:
            이 메서드는 실시간 스트리밍을 지원하기 위한 플레이스홀더입니다.
            구현 시:
            1. 각 노드의 결과를 yield
            2. 토큰 단위 스트리밍
            3. 진행 상황 업데이트
        """
        logger.info(f"Running pipeline with streaming for: '{query}'")

        # TODO: 스트리밍 구현
        # yield "검색 중..."
        # yield "관련성 판단 중..."
        # yield "답변 생성 중..."
        # yield response

        yield self.invoke(query, intent)

    def health_check(self) -> Dict[str, Any]:
        """
        파이프라인의 상태를 확인합니다.

        Returns:
            Dict: 상태 정보
        """
        logger.info("Performing pipeline health check")

        health_status = {
            "status": "healthy",
            "components": {
                "retriever": "ready",
                "relevance_evaluator": "ready",
                "web_searcher": "ready",
                "generator": "ready",
            },
            "config": {
                "max_retries": self.max_retries,
                "timeout": self.timeout,
                "debug": self.debug,
            },
        }

        # TODO: 실제 헬스 체크 로직
        # - 벡터 DB 연결 확인
        # - API 키 검증
        # - 메모리 상태 확인

        return health_status

