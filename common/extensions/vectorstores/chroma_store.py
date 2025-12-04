"""
Chroma 벡터 저장소 구현
=====================
ChromaDB를 사용한 벡터 저장소 실제 구현
"""

from typing import List, Dict, Any, Optional
import logging
from langchain_chroma import Chroma
from langchain_core.documents import Document

from common.base import BaseVectorStore, BaseEmbedding, RetrievalResult, RetrievalMode

logger = logging.getLogger(__name__)


class ChromaVectorStore(BaseVectorStore):
    """
    Chroma 기반 벡터 저장소
    
    기능:
    - 문서 저장 및 검색
    - 영구 저장 (persist)
    - 메타데이터 필터링
    - 로컬 및 클라우드 지원
    """
    
    def __init__(self,
                 embedding_model: BaseEmbedding,
                 persist_directory: str = "./chroma_db",
                 collection_name: str = "documents",
                 **kwargs):
        """
        Args:
            embedding_model: 임베딩 모델 인스턴스
            persist_directory: 저장 디렉토리
            collection_name: 컬렉션 이름
        """
        super().__init__(embedding_model, collection_name, **kwargs)
        
        self.persist_directory = persist_directory
        
        try:
            # Chroma 벡터 저장소 초기화
            from langchain_openai import OpenAIEmbeddings
            from langchain_community.embeddings import HuggingFaceEmbeddings
            
            # 임베딩 모델에 따라 LangChain 임베딩 객체 생성
            if hasattr(embedding_model, 'embedding_model'):
                # OpenAIEmbeddingModel 또는 HuggingFaceEmbeddingModel
                lc_embedding = embedding_model.embedding_model
            else:
                # 직접 임베딩 모델 객체
                lc_embedding = embedding_model
            
            # Chroma 벡터 저장소 생성
            self.vectorstore = Chroma(
                collection_name=collection_name,
                embedding_function=lc_embedding,
                persist_directory=persist_directory,
            )
            
            logger.info(f"✅ Chroma 벡터 저장소 초기화: {collection_name}")
            logger.info(f"   📁 저장 경로: {persist_directory}")
        
        except Exception as e:
            logger.error(f"❌ 벡터 저장소 초기화 실패: {e}")
            raise
    
    def add_documents(self, documents: List[Dict[str, Any]]) -> List[str]:
        """
        문서를 벡터 저장소에 추가
        
        Args:
            documents: 문서 리스트
                [
                    {
                        'id': 'doc_1',
                        'content': '문서 내용',
                        'metadata': {'source': 'file.pdf', ...}
                    },
                    ...
                ]
        
        Returns:
            추가된 문서 ID 리스트
        """
        try:
            if not documents:
                logger.warning("⚠️ 빈 문서 리스트")
                return []
            
            logger.info(f"📝 문서 추가 시작: {len(documents)}개")
            
            # Document 객체 생성
            doc_objects = []
            doc_ids = []
            
            for doc in documents:
                doc_id = doc.get('id', f"doc_{len(doc_objects)}")
                content = doc.get('content', '')
                metadata = doc.get('metadata', {})
                
                # LangChain Document 객체 생성
                lc_doc = Document(
                    page_content=content,
                    metadata=metadata
                )
                
                doc_objects.append(lc_doc)
                doc_ids.append(doc_id)
            
            # Chroma에 추가
            self.vectorstore.add_documents(
                doc_objects,
                ids=doc_ids
            )
            
            # 영구 저장
            self.vectorstore.persist()
            
            logger.info(f"✅ {len(doc_ids)}개 문서 추가 완료")
            
            return doc_ids
        
        except Exception as e:
            logger.error(f"❌ 문서 추가 오류: {e}")
            raise
    
    def search(self, query: str, top_k: int = 5) -> List[RetrievalResult]:
        """
        쿼리로 유사 문서 검색
        
        Args:
            query: 검색 쿼리
            top_k: 반환할 문서 개수
        
        Returns:
            검색 결과 리스트
        """
        try:
            logger.info(f"🔍 검색: '{query}' (top_k={top_k})")
            
            # 유사도 검색 (거리 포함)
            results = self.vectorstore.similarity_search_with_score(query, k=top_k)
            
            # RetrievalResult로 변환
            retrieval_results = []
            
            for i, (doc, distance) in enumerate(results):
                # 거리를 유사도로 변환 (Chroma는 cosine distance 사용)
                # similarity = 1 - distance
                similarity_score = max(0.0, 1.0 - distance)
                
                result = RetrievalResult(
                    document_id=f"doc_{i}",
                    content=doc.page_content,
                    score=similarity_score,
                    metadata=doc.metadata,
                    retrieval_mode=RetrievalMode.SIMILARITY,
                )
                
                retrieval_results.append(result)
                
                logger.debug(f"  [{i+1}] 유사도: {similarity_score:.4f}")
            
            logger.info(f"✅ 검색 완료: {len(retrieval_results)}개 결과")
            
            return retrieval_results
        
        except Exception as e:
            logger.error(f"❌ 검색 오류: {e}")
            raise
    
    def search_with_metadata_filter(self,
                                   query: str,
                                   filter_dict: Dict[str, Any],
                                   top_k: int = 5) -> List[RetrievalResult]:
        """
        메타데이터 필터를 포함한 검색
        
        Args:
            query: 검색 쿼리
            filter_dict: 메타데이터 필터
                예: {"source": "medical_document"}
            top_k: 반환할 문서 개수
        
        Returns:
            필터링된 검색 결과
        """
        try:
            logger.info(f"🔍 필터 검색: '{query}' (필터: {filter_dict})")
            
            # 필터를 포함한 검색
            results = self.vectorstore.similarity_search_with_score(
                query,
                k=top_k,
                filter=filter_dict
            )
            
            # RetrievalResult로 변환
            retrieval_results = []
            for i, (doc, distance) in enumerate(results):
                similarity_score = max(0.0, 1.0 - distance)
                
                result = RetrievalResult(
                    document_id=f"doc_{i}",
                    content=doc.page_content,
                    score=similarity_score,
                    metadata=doc.metadata,
                    retrieval_mode=RetrievalMode.SIMILARITY,
                )
                
                retrieval_results.append(result)
            
            logger.info(f"✅ 필터 검색 완료: {len(retrieval_results)}개 결과")
            
            return retrieval_results
        
        except Exception as e:
            logger.error(f"❌ 필터 검색 오류: {e}")
            raise
    
    def delete_documents(self, doc_ids: List[str]) -> bool:
        """
        문서 삭제
        
        Args:
            doc_ids: 삭제할 문서 ID 리스트
        
        Returns:
            성공 여부
        """
        try:
            if not doc_ids:
                return True
            
            logger.info(f"🗑️ 문서 삭제: {len(doc_ids)}개")
            
            # 문서 삭제
            self.vectorstore.delete(ids=doc_ids)
            
            # 영구 저장
            self.vectorstore.persist()
            
            logger.info(f"✅ 삭제 완료")
            
            return True
        
        except Exception as e:
            logger.error(f"❌ 삭제 오류: {e}")
            return False
    
    def clear(self) -> bool:
        """
        모든 문서 삭제
        
        Returns:
            성공 여부
        """
        try:
            logger.warning("🗑️ 모든 문서 삭제 시작")
            
            # 컬렉션 삭제 (다시 생성)
            self.vectorstore._collection.delete(
                where={}  # 모든 문서
            )
            
            # 영구 저장
            self.vectorstore.persist()
            
            logger.info(f"✅ 모든 문서 삭제 완료")
            
            return True
        
        except Exception as e:
            logger.error(f"❌ 초기화 오류: {e}")
            return False
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """
        컬렉션 통계 반환
        
        Returns:
            {
                'document_count': int,
                'collection_name': str,
                'embedding_dimension': int,
            }
        """
        try:
            collection = self.vectorstore._collection
            
            return {
                'document_count': collection.count(),
                'collection_name': collection.name,
                'embedding_dimension': len(self.embedding_model.get_embedding_dimension()),
            }
        
        except Exception as e:
            logger.error(f"❌ 통계 조회 오류: {e}")
            return {}


# ========== 팩토리 함수 ==========
def create_chroma_store(embedding_model: BaseEmbedding,
                       persist_directory: str = "./chroma_db",
                       collection_name: str = "documents",
                       **kwargs) -> ChromaVectorStore:
    """
    Chroma 벡터 저장소 생성
    
    Args:
        embedding_model: 임베딩 모델
        persist_directory: 저장 경로
        collection_name: 컬렉션 이름
        **kwargs: 추가 파라미터
        
    Returns:
        ChromaVectorStore 인스턴스
    """
    return ChromaVectorStore(
        embedding_model=embedding_model,
        persist_directory=persist_directory,
        collection_name=collection_name,
        **kwargs
    )

