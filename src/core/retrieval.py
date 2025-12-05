"""
Retrieval 모듈
Top-K 검색 및 similarity score 반환
"""
from typing import List, Tuple
from langchain_core.documents import Document
from langchain_chroma import Chroma
from langchain_core.retrievers import BaseRetriever
from pydantic import ConfigDict, Field
from src.utils import get_logger

logger = get_logger(__name__)


class SimpleRetriever(BaseRetriever):
    """
    단순 Top-K Retriever
    상위 K개 문서를 similarity score와 함께 반환
    """
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    # Pydantic 필드 선언
    vectorstore: Chroma = Field(..., description="Chroma 벡터스토어")
    top_k: int = Field(default=5, description="반환할 상위 문서 수")
    
    def __init__(
        self,
        vectorstore: Chroma,
        top_k: int = 5,
        **kwargs
    ):
        """
        Args:
            vectorstore: Chroma 벡터스토어
            top_k: 반환할 상위 문서 수 (기본값: 5)
        """
        super().__init__(
            vectorstore=vectorstore,
            top_k=top_k,
            **kwargs
        )
    
    def _get_relevant_documents(self, query: str) -> List[Document]:
        """
        BaseRetriever의 추상 메서드 구현
        상위 top_k개 문서를 반환 (점수는 메타데이터에 저장)
        
        Args:
            query: 검색 쿼리
            
        Returns:
            Document 리스트 (최대 top_k개)
        """
        logger.debug(f"문서 검색: {query}")
        
        # similarity_search_with_score로 점수와 함께 검색
        results = self.vectorstore.similarity_search_with_score(query, k=self.top_k)
        
        # 문서에 similarity score 메타데이터로 저장
        docs = []
        for doc, distance in results:
            # Chroma distance를 similarity score로 변환 (cosine distance)
            # similarity = 1 - distance
            similarity_score = 1.0 - distance if distance <= 1.0 else max(0.0, 1.0 - distance)
            doc.metadata['similarity_score'] = similarity_score
            docs.append(doc)
        
        logger.debug(f"검색 완료: {len(docs)}개 문서 반환")
        return docs
    
    def retrieve_with_scores(self, query: str) -> List[Tuple[Document, float]]:
        """
        문서와 점수를 함께 반환하는 메서드
        
        Args:
            query: 검색 쿼리
            
        Returns:
            (Document, similarity_score) 튜플 리스트
        """
        results = self.vectorstore.similarity_search_with_score(query, k=self.top_k)
        
        doc_scores = []
        for doc, distance in results:
            similarity_score = 1.0 - distance if distance <= 1.0 else max(0.0, 1.0 - distance)
            doc.metadata['similarity_score'] = similarity_score
            doc_scores.append((doc, similarity_score))
        
        return doc_scores
    
    def retrieve(self, query: str) -> List[Document]:
        """
        호환성을 위한 retrieve 메서드
        """
        return self._get_relevant_documents(query)
    
    def invoke(self, query: str) -> List[Document]:
        """
        LangChain 호환성을 위한 invoke 메서드
        """
        return self._get_relevant_documents(query)


def create_retriever(
    vectorstore: Chroma,
    top_k: int = 5,
    **kwargs
) -> BaseRetriever:
    """
    Retriever 생성
    
    Args:
        vectorstore: Chroma 벡터스토어
        top_k: 반환할 상위 문서 수 (기본값: 5)
        **kwargs: 호환성을 위한 추가 파라미터 (무시됨)
        
    Returns:
        SimpleRetriever 객체
    """
    logger.info(f"Retriever 생성: top_k={top_k}")
    return SimpleRetriever(
        vectorstore=vectorstore,
        top_k=top_k
    )

