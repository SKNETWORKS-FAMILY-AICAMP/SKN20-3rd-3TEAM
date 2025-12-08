"""
Vector Store Manager Module
임베딩 생성 및 벡터 DB 관리

역할:
  - 청크 텍스트를 임베딩 벡터로 변환
  - 벡터를 DB에 인덱싱 및 저장
  - 검색 시 유사 문서 검색
  - DB 생명주기 관리 (생성, 업데이트, 삭제)
"""

import os
import time
from typing import List, Dict, Tuple, Optional
import hashlib
import warnings
warnings.filterwarnings("ignore")

from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document

load_dotenv()

# API 키 확인
if not os.environ.get('OPENAI_API_KEY'):
    raise ValueError('.env 확인하세요. OPENAI_API_KEY가 없습니다')


class VectorStoreManager:
    """
    벡터 저장소를 관리하는 클래스
    
    책임:
        1. 임베딩 모델 초기화
        2. 청크 텍스트 → 벡터 변환
        3. 벡터 DB 관리
        4. 유사도 검색
    """
    
    def __init__(
        self, 
        collection_name: str = "pet_health_qa_system",
        persist_directory: str = "./chroma_db",
        embedding_model: str = "text-embedding-3-small"
    ):
        """
        VectorStoreManager 초기화
        
        Args:
            collection_name: Chroma 컬렉션 이름
            persist_directory: 벡터 DB 저장 경로
            embedding_model: OpenAI 임베딩 모델명
        """
        self.collection_name = collection_name
        self.persist_directory = persist_directory
        self.embedding_function = OpenAIEmbeddings(model=embedding_model)
        self.vector_db = None
        
        print(f"✓ [VectorStoreManager] 초기화 완료: {collection_name}")
    
    
    def create_vectorstore(self, documents: List[Document], batch_size: int = 100) -> bool:
        """
        문서들로부터 벡터스토어 생성
        
        Args:
            documents: Document 객체 리스트
            batch_size: 배치 처리 크기
            
        Returns:
            bool: 성공 여부
        """
        try:
            print(f"\n벡터스토어 생성 시작: {len(documents)}개 문서")
            
            # 첫 번째 배치로 벡터스토어 생성
            first_batch = documents[:batch_size]
            
            self.vector_db = Chroma.from_documents(
                documents=first_batch,
                embedding=self.embedding_function,
                collection_name=self.collection_name,
                persist_directory=self.persist_directory,
            )
            
            print(f"첫 번째 배치 완료: {len(first_batch)}개 문서")
            
            # 나머지 문서들을 배치로 추가
            remaining_docs = documents[batch_size:]
            total_batches = len(remaining_docs) // batch_size + (1 if len(remaining_docs) % batch_size > 0 else 0)
            
            for i in range(0, len(remaining_docs), batch_size):
                batch_num = i // batch_size + 2
                batch = remaining_docs[i:i + batch_size]
                
                print(f"배치 {batch_num}/{total_batches + 1} 처리 중... ({len(batch)}개 문서)")
                
                try:
                    self.vector_db.add_documents(batch)
                    print(f"배치 {batch_num} 완료!")
                    time.sleep(1)  # API 호출 제한 방지
                    
                except Exception as e:
                    print(f"배치 {batch_num} 에러: {e}")
                    # 더 작은 배치로 재시도
                    smaller_batches = [batch[j:j+20] for j in range(0, len(batch), 20)]
                    for small_batch in smaller_batches:
                        try:
                            self.vector_db.add_documents(small_batch)
                            time.sleep(0.5)
                        except Exception as small_e:
                            print(f"소 배치 에러: {small_e}")
            
            print("벡터스토어 생성 완료!")
            print(f"저장 경로: {self.persist_directory}")
            print(f"컬렉션명: {self.collection_name}")
            return True
            
        except Exception as e:
            print(f"벡터스토어 생성 실패: {e}")
            return False
    
    
    def load_vectorstore(self) -> bool:
        """
        기존 벡터스토어 로드
        
        Returns:
            bool: 성공 여부
        """
        try:
            self.vector_db = Chroma(
                persist_directory=self.persist_directory,
                collection_name=self.collection_name,
                embedding_function=self.embedding_function
            )
            print(f"✓ 벡터스토어 로드 성공: {self.collection_name}")
            return True
        except Exception as e:
            print(f"벡터스토어 로드 실패: {e}")
            return False
    
    
    def embed_and_index_chunks(self, chunks: List[Document]) -> bool:
        """
        여러 청크를 임베딩하고 벡터 DB에 인덱싱
        
        Args:
            chunks: Document 객체 리스트
            
        Returns:
            bool: 성공 여부
        """
        return self.create_vectorstore(chunks)
    
    
    def get_retriever(self, search_type: str = "similarity", k: int = 5):
        """
        리트리버 객체 반환
        
        Args:
            search_type: 검색 타입 (similarity, mmr 등)
            k: 검색할 문서 개수
            
        Returns:
            Retriever 객체
        """
        if self.vector_db is None:
            if not self.load_vectorstore():
                raise ValueError("벡터스토어를 로드할 수 없습니다.")
        
        return self.vector_db.as_retriever(
            search_type=search_type,
            search_kwargs={"k": k}
        )
    
    
    def search_similar_chunks(
        self,
        query: str,
        top_k: int = 5,
        threshold: float = 0.5
    ) -> List[Document]:
        """
        쿼리와 유사한 청크 검색
        
        Args:
            query: 검색 쿼리
            top_k: 반환할 상위 K개 결과
            threshold: 유사도 임계값 (사용 안 함)
        
        Returns:
            List[Document]: 검색된 Document 리스트
        """
        if self.vector_db is None:
            if not self.load_vectorstore():
                return []
        
        print(f"🔍 [search_similar_chunks] 유사도 검색: '{query}' (top_k={top_k})")
        
        try:
            results = self.vector_db.similarity_search(query, k=top_k)
            print(f"✓ {len(results)}개 문서 검색됨")
            return results
        except Exception as e:
            print(f"검색 실패: {e}")
            return []
    
    
    def delete_chunk_by_id(self, chunk_id: str) -> bool:
        """
        특정 ID의 청크 삭제
        
        Args:
            chunk_id (str): 삭제할 청크의 고유 ID
            
        Returns:
            bool: 성공 여부
        
        TODO:
            - self.vector_db.delete([chunk_id])
        """
        print(f"🗑️  [delete_chunk_by_id] 청크 삭제: {chunk_id}")
        return True
    
    
    def clear_collection(self) -> bool:
        """
        전체 컬렉션 초기화
        
        Args:
            (없음)
            
        Returns:
            bool: 성공 여부
        
        주의: 이 작업은 돌이킬 수 없습니다!
        
        TODO:
            - self.vector_db.delete_collection(self.collection_name)
            - 새로운 컬렉션 재생성
        """
        print(f"⚠️  [clear_collection] 컬렉션 초기화: {self.collection_name}")
        return True
    
    
    def get_stats(self) -> Dict[str, any]:
        """
        벡터 DB 통계 조회
        
        Returns:
            Dict: DB 통계 정보
                {
                    'total_chunks': 0,
                    'embedding_model': 'model_name',
                    'embedding_dim': 768,
                    'collection_name': 'name',
                    'last_updated': '2025-12-05 10:30:00'
                }
        
        TODO:
            - self.vector_db.get_collection(self.collection_name).count()
        """
        stats = {
            'total_chunks': 0,
            'embedding_model': self.model_name,
            'embedding_dim': self.embedding_dim,
            'collection_name': self.collection_name,
            'status': 'initialized'
        }
        
        print(f"📊 [get_stats] DB 통계: {stats}")
        return stats


def embed_and_index_chunks(chunks: List[str]) -> bool:
    """
    모듈 수준 함수: 청크 임베딩 및 인덱싱
    
    Args:
        chunks (List[str]): 인덱싱할 텍스트 청크 리스트
        
    Returns:
        bool: 성공 여부
    
    역할:
        - VectorStoreManager 인스턴스 생성 또는 기존 인스턴스 사용
        - 청크 임베딩 및 DB 저장
        - 성공 여부 반환
    
    TODO:
        - 싱글톤 패턴으로 manager 관리
        - 또는 전역 manager 객체 사용
    """
    print("\n" + "="*60)
    print("🔄 [embed_and_index_chunks] 청크 임베딩 및 인덱싱")
    print("="*60 + "\n")
    
    # VectorStoreManager 인스턴스 생성
    manager = VectorStoreManager()
    
    # 청크 임베딩 및 인덱싱
    success = manager.embed_and_index_chunks(chunks)
    
    print("="*60)
    if success:
        print("✅ 임베딩 및 인덱싱 완료")
    else:
        print("❌ 임베딩 및 인덱싱 실패")
    print("="*60 + "\n")
    
    return success


# ==================== 엔트리 포인트 ====================
if __name__ == "__main__":
    """
    테스트 실행 (스켈레톤 데모)
    """
    
    print("\n" + "="*60)
    print("📦 Vector Store Manager Module - 테스트")
    print("="*60 + "\n")
    
    # 테스트 1: VectorStoreManager 초기화
    print("### 테스트 1: VectorStoreManager 초기화 ###\n")
    manager = VectorStoreManager()
    stats = manager.get_stats()
    print(f"✓ 초기화 완료: {stats}\n")
    
    # 테스트 2: 단일 청크 임베딩
    print("### 테스트 2: 단일 청크 임베딩 ###\n")
    sample_chunk = "강아지 피부염은 가려움증을 유발합니다"
    embedding = manager.embed_chunk(sample_chunk)
    print(f"✓ 임베딩 생성 완료 (크기: {len(embedding)})\n")
    
    # 테스트 3: 배치 임베딩 및 인덱싱
    print("### 테스트 3: 배치 임베딩 및 인덱싱 ###\n")
    test_chunks = [
        "강아지 피부염 증상",
        "치료 방법 안내",
        "병원 방문 가이드"
    ]
    success = manager.embed_and_index_chunks(test_chunks)
    print(f"✓ 인덱싱 결과: {success}\n")
    
    # 테스트 4: 유사도 검색
    print("### 테스트 4: 유사도 검색 ###\n")
    search_results = manager.search_similar_chunks("피부 질환 치료", top_k=3)
    print(f"✓ 검색 완료: {len(search_results)}개 결과\n")
    
    # 테스트 5: 모듈 수준 함수
    print("### 테스트 5: 모듈 수준 함수 ###\n")
    test_chunks_2 = ["청크1", "청크2", "청크3"]
    embed_and_index_chunks(test_chunks_2)
    
    print("="*60)
    print("✅ 테스트 완료!")
    print("="*60)

