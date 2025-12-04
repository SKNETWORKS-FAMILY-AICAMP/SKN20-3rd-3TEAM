"""
Chroma 기반 검색기 구현
===================
Chroma 벡터 저장소를 사용한 검색기 실제 구현
"""

from typing import List, Dict, Any, Optional
import logging

from common.base import BaseRetriever, BaseVectorStore, RetrievalResult, RetrievalMode

logger = logging.getLogger(__name__)


class SimpleTopKRetriever(BaseRetriever):
    """
    단순 Top-K 검색기
    
    기능:
    - 상위 K개 문서 반환
    - 유사도 점수 포함
    - 메타데이터 필터링
    """
    
    def __init__(self,
                 vector_store: BaseVectorStore,
                 top_k: int = 5,
                 min_score: float = 0.0,
                 **kwargs):
        """
        Args:
            vector_store: 벡터 저장소
            top_k: 반환할 상위 문서 수
            min_score: 최소 유사도 점수
        """
        super().__init__(vector_store, **kwargs)
        self.top_k = top_k
        self.min_score = min_score
        
        logger.info(f"✅ Simple Top-K 검색기 초기화: top_k={top_k}")
    
    def retrieve(self, query: str, top_k: Optional[int] = None, **kwargs) -> List[RetrievalResult]:
        """
        검색 실행
        
        Args:
            query: 검색 쿼리
            top_k: 반환할 문서 개수 (기본값 사용 시 None)
            **kwargs: 추가 옵션
                - min_score: 최소 유사도 점수 필터
        
        Returns:
            검색 결과 리스트
        """
        try:
            # 기본값 적용
            if top_k is None:
                top_k = self.top_k
            
            logger.info(f"🔍 검색: '{query}' (top_k={top_k})")
            
            # 벡터 저장소에서 검색
            results = self.vector_store.search(query, top_k=top_k * 2)  # 여유있게 검색
            
            # 최소 점수 필터링
            min_score = kwargs.get('min_score', self.min_score)
            filtered_results = [r for r in results if r.score >= min_score]
            
            # Top-K 반환
            final_results = filtered_results[:top_k]
            
            logger.info(f"✅ 검색 완료: {len(final_results)}개 결과")
            
            return final_results
        
        except Exception as e:
            logger.error(f"❌ 검색 오류: {e}")
            raise
    
    def set_top_k(self, top_k: int):
        """Top-K 값 변경"""
        self.top_k = top_k
        logger.info(f"⚙️ Top-K 변경: {top_k}")


class FilteredRetriever(BaseRetriever):
    """
    메타데이터 필터를 포함한 검색기
    
    기능:
    - 메타데이터 기반 필터링
    - 카테고리별 검색
    - 소스별 검색
    """
    
    def __init__(self,
                 vector_store: BaseVectorStore,
                 top_k: int = 5,
                 **kwargs):
        """
        Args:
            vector_store: 벡터 저장소
            top_k: 반환할 상위 문서 수
        """
        super().__init__(vector_store, **kwargs)
        self.top_k = top_k
        
        logger.info(f"✅ 필터 검색기 초기화: top_k={top_k}")
    
    def retrieve(self, query: str, top_k: Optional[int] = None, **kwargs) -> List[RetrievalResult]:
        """
        메타데이터 필터를 포함한 검색
        
        Args:
            query: 검색 쿼리
            top_k: 반환할 문서 개수
            **kwargs: 추가 옵션
                - metadata_filter: 메타데이터 필터 {'source': 'medical', ...}
        
        Returns:
            검색 결과 리스트
        """
        try:
            if top_k is None:
                top_k = self.top_k
            
            # 메타데이터 필터 추출
            metadata_filter = kwargs.get('metadata_filter', {})
            
            logger.info(f"🔍 필터 검색: '{query}'")
            if metadata_filter:
                logger.info(f"   필터: {metadata_filter}")
            
            # Chroma의 필터 검색 사용
            if hasattr(self.vector_store, 'search_with_metadata_filter') and metadata_filter:
                results = self.vector_store.search_with_metadata_filter(
                    query,
                    metadata_filter,
                    top_k=top_k
                )
            else:
                # 필터 없이 검색
                results = self.vector_store.search(query, top_k=top_k)
            
            logger.info(f"✅ 검색 완료: {len(results)}개 결과")
            
            return results
        
        except Exception as e:
            logger.error(f"❌ 필터 검색 오류: {e}")
            raise


class MMRRetriever(BaseRetriever):
    """
    MMR (Maximum Marginal Relevance) 검색기
    
    기능:
    - 다양성을 고려한 문서 선택
    - 중복 제거
    - 다양한 관점의 문서 검색
    """
    
    def __init__(self,
                 vector_store: BaseVectorStore,
                 top_k: int = 5,
                 lambda_mult: float = 0.5,
                 **kwargs):
        """
        Args:
            vector_store: 벡터 저장소
            top_k: 반환할 문서 개수
            lambda_mult: 다양성 계수 (0~1, 0=다양성 중심, 1=관련성 중심)
        """
        super().__init__(vector_store, **kwargs)
        self.top_k = top_k
        self.lambda_mult = lambda_mult
        
        logger.info(f"✅ MMR 검색기 초기화: top_k={top_k}, lambda={lambda_mult}")
    
    def retrieve(self, query: str, top_k: Optional[int] = None, **kwargs) -> List[RetrievalResult]:
        """
        MMR 검색 실행
        
        Args:
            query: 검색 쿼리
            top_k: 반환할 문서 개수
            **kwargs: 추가 옵션
                - lambda_mult: 다양성 계수 오버라이드
        
        Returns:
            다양성을 고려한 검색 결과
        """
        try:
            if top_k is None:
                top_k = self.top_k
            
            lambda_mult = kwargs.get('lambda_mult', self.lambda_mult)
            
            logger.info(f"🔍 MMR 검색: '{query}' (top_k={top_k}, lambda={lambda_mult})")
            
            # 기본 검색으로 더 많은 결과 가져오기
            initial_results = self.vector_store.search(query, top_k=top_k * 3)
            
            # MMR 알고리즘 적용
            selected = []
            remaining = list(initial_results)
            
            for _ in range(min(top_k, len(remaining))):
                if not remaining:
                    break
                
                # 첫 번째 반복 또는 선택된 문서가 없으면 가장 관련성 높은 문서 선택
                if not selected:
                    # 가장 높은 점수의 문서 선택
                    best_idx = 0
                    best_score = remaining[0].score
                    
                    for i, result in enumerate(remaining):
                        if result.score > best_score:
                            best_score = result.score
                            best_idx = i
                    
                    selected.append(remaining.pop(best_idx))
                else:
                    # MMR: 관련성과 다양성 균형
                    best_idx = 0
                    best_mmr_score = -float('inf')
                    
                    for i, candidate in enumerate(remaining):
                        # 관련성 점수
                        relevance_score = candidate.score
                        
                        # 다양성 점수 (선택된 문서와의 최소 거리)
                        min_diversity = float('inf')
                        for selected_doc in selected:
                            # 간단한 다양성 계산 (내용 길이 차이)
                            diversity = abs(
                                len(candidate.content) - len(selected_doc.content)
                            ) / max(1, max(len(candidate.content), len(selected_doc.content)))
                            min_diversity = min(min_diversity, diversity)
                        
                        # MMR 점수 = λ * 관련성 + (1-λ) * 다양성
                        mmr_score = (
                            lambda_mult * relevance_score +
                            (1 - lambda_mult) * min_diversity
                        )
                        
                        if mmr_score > best_mmr_score:
                            best_mmr_score = mmr_score
                            best_idx = i
                    
                    selected.append(remaining.pop(best_idx))
            
            logger.info(f"✅ MMR 검색 완료: {len(selected)}개 결과")
            
            return selected
        
        except Exception as e:
            logger.error(f"❌ MMR 검색 오류: {e}")
            raise


# ========== 팩토리 함수 ==========
def create_retriever(retriever_type: str = "simple",
                    vector_store: BaseVectorStore = None,
                    top_k: int = 5,
                    **kwargs) -> BaseRetriever:
    """
    검색기 생성
    
    Args:
        retriever_type: 검색기 타입 (simple, filtered, mmr)
        vector_store: 벡터 저장소
        top_k: 반환할 문서 개수
        **kwargs: 추가 파라미터
        
    Returns:
        검색기 인스턴스
    """
    if retriever_type.lower() == "simple":
        return SimpleTopKRetriever(
            vector_store=vector_store,
            top_k=top_k,
            **kwargs
        )
    
    elif retriever_type.lower() == "filtered":
        return FilteredRetriever(
            vector_store=vector_store,
            top_k=top_k,
            **kwargs
        )
    
    elif retriever_type.lower() == "mmr":
        lambda_mult = kwargs.pop('lambda_mult', 0.5)
        return MMRRetriever(
            vector_store=vector_store,
            top_k=top_k,
            lambda_mult=lambda_mult,
            **kwargs
        )
    
    else:
        raise ValueError(f"지원하지 않는 검색기 타입: {retriever_type}")

