"""
쿼리 오케스트레이터

전체 시스템의 워크플로우를 조정합니다.
"""

from typing import Any, Dict

from src.classifier.question_classifier import QuestionClassifier
from src.config.logger import get_logger
from src.mapping.hospital_mapper import HospitalMapper
from src.rag.langgraph_crag_pipeline import LangGraphRAGPipeline
from src.types.response import ErrorResponse, HospitalResponse, RAGResponse
from src.web.general_web_searcher import GeneralWebSearcher

logger = get_logger(__name__)


class QueryOrchestrator:
    """
    전체 시스템 오케스트레이터

    사용자 질문을 분류하고, 적절한 처리 파이프라인으로 라우팅합니다.

    워크플로우:
    1. QuestionClassifier: 질문 의도 분류
    2. 의도별 처리:
       - "medical": LangGraphRAGPipeline 사용
       - "hospital": HospitalMapper 사용
       - "general": GeneralWebSearcher 사용
       - "unknown": 기본 처리
    """

    def __init__(self):
        """오케스트레이터 초기화"""
        self.classifier = QuestionClassifier()
        self.rag_pipeline = LangGraphRAGPipeline()
        self.hospital_mapper = HospitalMapper()
        self.web_searcher = GeneralWebSearcher()

        logger.info("QueryOrchestrator initialized")

    def process(self, query: str) -> Dict[str, Any]:
        """
        사용자 질문을 처리합니다.

        Args:
            query: 사용자 질문

        Returns:
            Dict: 처리 결과
                - type: 응답 타입 ("rag", "hospital", "error")
                - data: 실제 응답 (RAGResponse, HospitalResponse, ErrorResponse)

        Note:
            이 메서드는 전체 시스템의 진입점입니다.
            의도 분류 → 해당 처리기 호출 → 결과 반환
        """
        import time

        start_time = time.time()
        logger.info(f"Processing query: '{query}'")

        try:
            # 1. 의도 분류
            classification = self.classifier.classify(query)
            intent = classification.intent
            confidence = classification.confidence

            logger.info(
                f"Query classified as '{intent}' (confidence: {confidence:.2f})"
            )

            # 2. 의도별 처리
            if intent == "medical":
                result = self._process_medical_query(query, classification)

            elif intent == "hospital":
                result = self._process_hospital_query(query, classification)

            elif intent == "general":
                result = self._process_general_query(query, classification)

            else:
                result = self._process_unknown_query(query, classification)

            # 실행 시간 추가
            elapsed = time.time() - start_time
            if hasattr(result.get("data"), "execution_time"):
                result["data"].execution_time = elapsed

            logger.info(f"Query processing completed in {elapsed:.2f}s")
            return result

        except Exception as e:
            logger.error(f"Query processing error: {str(e)}")
            error_response = ErrorResponse(
                error_code="ORCHESTRATION_ERROR",
                error_message=str(e),
                details={"query": query},
            )
            return {"type": "error", "data": error_response}

    def _process_medical_query(
        self, query: str, classification: Any
    ) -> Dict[str, Any]:
        """의료 질문 처리"""
        logger.info("Processing medical query")

        try:
            response = self.rag_pipeline.invoke(query, intent="medical")
            return {"type": "rag", "data": response}

        except Exception as e:
            logger.error(f"Medical query processing failed: {str(e)}")
            return {
                "type": "error",
                "data": ErrorResponse(
                    error_code="MEDICAL_QUERY_FAILED",
                    error_message=str(e),
                ),
            }

    def _process_hospital_query(
        self, query: str, classification: Any
    ) -> Dict[str, Any]:
        """병원 정보 질문 처리"""
        logger.info("Processing hospital query")

        try:
            # 위치 추출 및 병원 검색
            mapper_result = self.hospital_mapper.extract_and_search(query)

            if not mapper_result["success"]:
                # 위치 추출 실패시 일반 웹 검색으로 폴백
                logger.info("Hospital mapper failed, using general web search")
                search_results = self.web_searcher.search(query)

                response = HospitalResponse(
                    query=query,
                    hospitals=search_results,
                    location={},
                    metadata={"source": "web_search"},
                )
            else:
                response = HospitalResponse(
                    query=query,
                    hospitals=mapper_result["hospitals"],
                    location=mapper_result["location"],
                    metadata={
                        "coordinates": mapper_result["coordinates"],
                        "source": "hospital_mapper",
                    },
                )

            return {"type": "hospital", "data": response}

        except Exception as e:
            logger.error(f"Hospital query processing failed: {str(e)}")
            return {
                "type": "error",
                "data": ErrorResponse(
                    error_code="HOSPITAL_QUERY_FAILED",
                    error_message=str(e),
                ),
            }

    def _process_general_query(
        self, query: str, classification: Any
    ) -> Dict[str, Any]:
        """일반 정보 질문 처리"""
        logger.info("Processing general query")

        try:
            # 웹 검색 수행
            search_results = self.web_searcher.search(query)

            # 일반 쿼리도 RAGResponse로 반환
            response = RAGResponse(
                query=query,
                answer="다음은 웹 검색 결과입니다:\n\n" +
                "\n".join([r.get("snippet", "") for r in search_results[:3]]),
                documents=[],
                intent="general",
                metadata={
                    "web_search_results": search_results,
                    "source": "general_web_search",
                },
            )

            return {"type": "rag", "data": response}

        except Exception as e:
            logger.error(f"General query processing failed: {str(e)}")
            return {
                "type": "error",
                "data": ErrorResponse(
                    error_code="GENERAL_QUERY_FAILED",
                    error_message=str(e),
                ),
            }

    def _process_unknown_query(
        self, query: str, classification: Any
    ) -> Dict[str, Any]:
        """미분류 질문 처리"""
        logger.info("Processing unknown query")

        try:
            # 폴백: 일반 웹 검색 수행
            search_results = self.web_searcher.search(query)

            response = RAGResponse(
                query=query,
                answer="질문을 정확히 분류하지 못했습니다. 다음은 웹 검색 결과입니다:\n\n" +
                "\n".join([r.get("snippet", "") for r in search_results[:3]]),
                documents=[],
                intent="unknown",
                metadata={
                    "web_search_results": search_results,
                    "source": "fallback_web_search",
                },
            )

            return {"type": "rag", "data": response}

        except Exception as e:
            logger.error(f"Unknown query processing failed: {str(e)}")
            return {
                "type": "error",
                "data": ErrorResponse(
                    error_code="UNKNOWN_QUERY_FAILED",
                    error_message="질문 처리 중 오류가 발생했습니다.",
                ),
            }

    def get_statistics(self) -> Dict[str, Any]:
        """
        시스템 통계를 반환합니다.

        Returns:
            Dict: 통계 정보
        """
        # TODO: 실제 통계 수집 로직 구현
        return {
            "total_queries": 0,
            "by_intent": {
                "medical": 0,
                "hospital": 0,
                "general": 0,
                "unknown": 0,
            },
            "success_rate": 0.0,
            "average_response_time": 0.0,
        }

