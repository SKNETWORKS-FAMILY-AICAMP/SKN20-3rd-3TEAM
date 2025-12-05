"""
Vector Store Manager Module
임베딩 생성 및 벡터 DB 관리

역할:
  - 청크 텍스트를 임베딩 벡터로 변환
  - 벡터를 DB에 인덱싱 및 저장
  - 검색 시 유사 문서 검색
  - DB 생명주기 관리 (생성, 업데이트, 삭제)
"""

from typing import List, Dict, Tuple, Optional
import hashlib


class VectorStoreManager:
    """
    벡터 저장소를 관리하는 클래스
    
    책임:
        1. 임베딩 모델 초기화
        2. 청크 텍스트 → 벡터 변환
        3. 벡터 DB 관리
        4. 유사도 검색
    """
    
    def __init__(self, model_name: str = "sentence-transformers/multilingual-e5-base"):
        """
        VectorStoreManager 초기화
        
        Args:
            model_name (str): 사용할 임베딩 모델 (기본값: multilingual-e5-base)
        
        속성:
            - embedding_model: 임베딩 모델 (로드되지 않은 상태)
            - vector_db: 벡터 DB 클라이언트 (Chroma)
            - collection_name: DB 컬렉션 이름
            - embedding_dim: 임베딩 차원 수 (보통 768)
        
        TODO:
            - embedding_model = SentenceTransformer(model_name) 로드
            - vector_db = chromadb.Client() 초기화
            - 기존 컬렉션 로드 또는 새로 생성
        """
        self.model_name = model_name
        self.embedding_model = None  # TODO: 모델 로드
        self.vector_db = None  # TODO: Chroma 클라이언트 초기화
        self.collection_name = "medical_documents"
        self.embedding_dim = 768
        
        print(f"✓ [VectorStoreManager] 초기화 완료: {model_name}")
    
    
    def embed_chunk(self, text: str) -> List[float]:
        """
        텍스트 청크를 임베딩 벡터로 변환
        
        Args:
            text (str): 변환할 텍스트 청크
            
        Returns:
            List[float]: 임베딩 벡터 (길이: embedding_dim)
        
        처리:
            1. 텍스트 정규화
            2. 임베딩 모델 호출
            3. 벡터 반환
            
        예시:
            입력: "강아지 피부염 증상은 가려움증입니다"
            출력: [0.123, 0.456, ..., -0.789]  (길이: 768)
        
        TODO:
            - embedding_model.encode(text) 호출
            - 벡터 정규화 (선택)
        """
        # TODO: 실제 임베딩 생성
        # embedding = self.embedding_model.encode(text)
        
        # 더미 벡터 생성 (768차원)
        hash_value = int(hashlib.md5(text.encode()).hexdigest(), 16)
        embedding = [(hash_value + i) % 1000 / 1000.0 for i in range(self.embedding_dim)]
        
        print(f"✓ [embed_chunk] {len(text)} 문자 텍스트 → {len(embedding)}차원 벡터")
        return embedding
    
    
    def embed_and_index_chunks(self, chunks: List[str]) -> bool:
        """
        여러 청크를 임베딩하고 벡터 DB에 인덱싱
        
        Args:
            chunks (List[str]): 인덱싱할 텍스트 청크 리스트
            
        Returns:
            bool: 성공 여부 (True: 성공, False: 실패)
        
        처리:
            1️⃣  [임베딩 생성] 각 청크를 벡터로 변환
            2️⃣  [ID 생성] 고유 ID 할당 (hash 기반)
            3️⃣  [메타데이터] 청크 정보 저장
            4️⃣  [DB 저장] 벡터와 메타데이터를 DB에 인덱싱
            5️⃣  [검증] 저장 성공 여부 확인
        
        예시:
            입력: ["청크1: 피부염...", "청크2: 치료 방법..."]
            
            처리:
            - 청크1 → 임베딩1 (ID: hash_abc123)
            - 청크2 → 임베딩2 (ID: hash_def456)
            
            출력: True (성공)
        
        TODO:
            - 청크별 임베딩 생성 루프
            - DB 저장 로직 (add_documents)
            - 예외 처리 (API 오류, DB 연결 오류)
        """
        # TODO: 배치 임베딩 생성
        # embeddings = [self.embed_chunk(chunk) for chunk in chunks]
        
        # TODO: DB 저장
        # self.vector_db.add_documents(
        #     documents=chunks,
        #     embeddings=embeddings,
        #     metadatas=[{...} for chunk in chunks]
        # )
        
        print(f"\n🔄 [embed_and_index_chunks] {len(chunks)}개 청크 인덱싱 시작\n")
        
        for idx, chunk in enumerate(chunks, 1):
            print(f"  [{idx}/{len(chunks)}] 임베딩 생성: {chunk[:50]}...")
            embedding = self.embed_chunk(chunk)
        
        print(f"\n✅ 인덱싱 완료: {len(chunks)}개 청크 저장됨\n")
        return True
    
    
    def search_similar_chunks(
        self,
        query: str,
        top_k: int = 5,
        threshold: float = 0.5
    ) -> List[Tuple[str, float]]:
        """
        쿼리와 유사한 청크 검색
        
        Args:
            query (str): 검색 쿼리
            top_k (int): 반환할 상위 K개 결과
            threshold (float): 유사도 임계값 (0.0-1.0)
        
        Returns:
            List[Tuple[str, float]]: [(청크_텍스트, 유사도_점수), ...]
                유사도 점수는 0.0 (완전히 다름) ~ 1.0 (동일)
        
        검색 과정:
            1. 쿼리를 임베딩으로 변환
            2. DB에서 유사도 검색 (cosine similarity)
            3. threshold 이상 결과만 필터링
            4. Top-K 결과 반환
        
        예시:
            입력: query="강아지 피부염", top_k=3
            
            출력:
            [
                ("피부염은 가려움증을 유발합니다", 0.92),
                ("강아지 질병 관리 방법", 0.78),
                ("동물병원 진료 안내", 0.62)
            ]
        
        TODO:
            - 쿼리 임베딩 생성
            - DB 유사도 검색
            - 결과 필터링 및 정렬
        """
        # TODO: 검색 로직
        # query_embedding = self.embed_chunk(query)
        # results = self.vector_db.search(query_embedding, top_k=top_k)
        
        print(f"🔍 [search_similar_chunks] 유사도 검색: '{query}' (top_k={top_k})\n")
        
        # 더미 결과
        dummy_results = [
            (f"검색 결과 {i+1}: {query} 관련 청크 텍스트...", 0.9 - i*0.1)
            for i in range(top_k)
        ]
        
        for chunk, score in dummy_results:
            print(f"  [{score:.2%}] {chunk[:50]}...")
        
        return dummy_results
    
    
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

