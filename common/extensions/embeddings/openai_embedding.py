"""
OpenAI Embeddings 구현
====================
OpenAI API를 사용한 임베딩 모델 실제 구현
"""

from typing import List, Optional
import logging
from langchain_openai import OpenAIEmbeddings

from common.base import BaseEmbedding

logger = logging.getLogger(__name__)


class OpenAIEmbeddingModel(BaseEmbedding):
    """
    OpenAI Embeddings 기반 임베딩 모델
    
    기능:
    - text-embedding-3-small (1536 차원)
    - text-embedding-3-large (3072 차원)
    - 배치 임베딩
    - 캐싱 지원
    """
    
    def __init__(self,
                 model_name: str = "text-embedding-3-small",
                 api_key: Optional[str] = None,
                 **kwargs):
        """
        Args:
            model_name: OpenAI 임베딩 모델 (small: 1536, large: 3072)
            api_key: OpenAI API 키 (없으면 환경변수에서 로드)
        """
        # 모델별 차원 설정
        if "small" in model_name:
            dimension = 1536
        elif "large" in model_name:
            dimension = 3072
        else:
            dimension = 1536
        
        super().__init__(model_name, dimension, **kwargs)
        
        try:
            # OpenAI Embeddings 초기화
            init_params = {"model": model_name}
            
            if api_key:
                init_params["api_key"] = api_key
            
            self.embedding_model = OpenAIEmbeddings(**init_params)
            
            logger.info(f"✅ OpenAI 임베딩 모델 초기화: {model_name} ({dimension}D)")
        
        except Exception as e:
            logger.error(f"❌ 임베딩 모델 초기화 실패: {e}")
            raise
    
    def embed_text(self, text: str) -> List[float]:
        """
        단일 텍스트를 임베딩
        
        Args:
            text: 임베딩할 텍스트
            
        Returns:
            임베딩 벡터 (float 리스트)
        """
        try:
            # 텍스트 정제
            text = text.strip()
            
            if not text:
                logger.warning("⚠️ 빈 텍스트 입력")
                return [0.0] * self.dimension
            
            # 임베딩 생성
            embedding = self.embedding_model.embed_query(text)
            
            logger.debug(f"✅ 임베딩 완료: {len(text)} 글자 → {len(embedding)}D")
            
            return embedding
        
        except Exception as e:
            logger.error(f"❌ 임베딩 오류: {e}")
            raise
    
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """
        배치 텍스트를 임베딩 (병렬 처리)
        
        Args:
            texts: 임베딩할 텍스트 리스트
            
        Returns:
            임베딩 벡터 리스트
        """
        try:
            if not texts:
                logger.warning("⚠️ 빈 텍스트 리스트")
                return []
            
            # 텍스트 정제
            cleaned_texts = [t.strip() for t in texts if t.strip()]
            
            logger.info(f"📦 배치 임베딩 시작: {len(cleaned_texts)}개 텍스트")
            
            # 배치 임베딩 생성
            embeddings = self.embedding_model.embed_documents(cleaned_texts)
            
            logger.info(f"✅ 배치 임베딩 완료: {len(embeddings)}개")
            
            return embeddings
        
        except Exception as e:
            logger.error(f"❌ 배치 임베딩 오류: {e}")
            raise
    
    def get_embedding_dimension(self) -> int:
        """임베딩 차원 반환"""
        return self.dimension


class HuggingFaceEmbeddingModel(BaseEmbedding):
    """
    HuggingFace Embeddings 기반 임베딩 모델
    
    특징:
    - 로컬 실행 (API 호출 불필요)
    - 한국어 지원이 좋은 모델
    - CPU/GPU 지원
    """
    
    def __init__(self,
                 model_name: str = "jhgan/ko-sroberta-multitask",
                 device: str = "cpu",
                 **kwargs):
        """
        Args:
            model_name: HuggingFace 모델 ID
            device: 실행 디바이스 (cpu, cuda)
        """
        # 기본 차원 설정 (대부분의 sentence-transformers 모델)
        dimension = 768  # 또는 모델별로 다를 수 있음
        
        super().__init__(model_name, dimension, **kwargs)
        
        try:
            from langchain_community.embeddings import HuggingFaceEmbeddings
            
            # HuggingFace Embeddings 초기화
            self.embedding_model = HuggingFaceEmbeddings(
                model_name=model_name,
                model_kwargs={'device': device},
                encode_kwargs={'normalize_embeddings': True}
            )
            
            logger.info(f"✅ HuggingFace 임베딩 모델 초기화: {model_name}")
        
        except Exception as e:
            logger.error(f"❌ HuggingFace 임베딩 초기화 실패: {e}")
            raise
    
    def embed_text(self, text: str) -> List[float]:
        """단일 텍스트 임베딩"""
        try:
            text = text.strip()
            
            if not text:
                logger.warning("⚠️ 빈 텍스트")
                return [0.0] * self.dimension
            
            embedding = self.embedding_model.embed_query(text)
            
            logger.debug(f"✅ HF 임베딩 완료: {len(text)} 글자 → {len(embedding)}D")
            
            return embedding
        
        except Exception as e:
            logger.error(f"❌ HF 임베딩 오류: {e}")
            raise
    
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """배치 임베딩"""
        try:
            if not texts:
                logger.warning("⚠️ 빈 텍스트 리스트")
                return []
            
            cleaned_texts = [t.strip() for t in texts if t.strip()]
            
            logger.info(f"📦 HF 배치 임베딩: {len(cleaned_texts)}개")
            
            embeddings = self.embedding_model.embed_documents(cleaned_texts)
            
            logger.info(f"✅ 완료: {len(embeddings)}개")
            
            return embeddings
        
        except Exception as e:
            logger.error(f"❌ HF 배치 오류: {e}")
            raise
    
    def get_embedding_dimension(self) -> int:
        """임베딩 차원"""
        return self.dimension


# ========== 팩토리 함수 ==========
def create_embedding(model_type: str = "openai",
                     model_name: Optional[str] = None,
                     **kwargs) -> BaseEmbedding:
    """
    임베딩 모델 생성
    
    Args:
        model_type: "openai" 또는 "huggingface"
        model_name: 모델 이름
        **kwargs: 추가 파라미터
        
    Returns:
        임베딩 모델 인스턴스
    """
    if model_type.lower() == "openai":
        if not model_name:
            model_name = "text-embedding-3-small"
        return OpenAIEmbeddingModel(model_name=model_name, **kwargs)
    
    elif model_type.lower() == "huggingface":
        if not model_name:
            model_name = "jhgan/ko-sroberta-multitask"
        return HuggingFaceEmbeddingModel(model_name=model_name, **kwargs)
    
    else:
        raise ValueError(f"지원하지 않는 모델 타입: {model_type}")

