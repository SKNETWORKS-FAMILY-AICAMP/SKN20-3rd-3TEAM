"""
확장 모듈 (Extensions)
===================
공통 모듈을 기반으로 팀원들이 고도화한 구현들을 담는 공간입니다.

각 팀원은 자신의 담당 영역에서 BaseXXX 클래스를 상속하여 구현합니다.
"""

# 예시 구현 (팀원들이 추가로 작성)
# from .embeddings import MyAdvancedEmbedding
# from .retrievers import MyRetriever
# from .pipelines import MyAdvancedPipeline

__all__ = [
    # 임베딩 모델
    # "MyAdvancedEmbedding",
    
    # 검색기
    # "MyRetriever",
    
    # 파이프라인
    # "MyAdvancedPipeline",
]

"""
사용 예시:

from common.extensions import MyAdvancedEmbedding, MyRetriever, MyAdvancedPipeline

# 각 컴포넌트 초기화
embedding = MyAdvancedEmbedding(model_name="best-model")
retriever = MyRetriever(vector_store=vector_store)
pipeline = MyAdvancedPipeline(
    retriever=retriever,
    embedding_model=embedding,
    vector_store=vector_store,
    llm_client=llm_client
)

# 처리
response = pipeline.process("사용자 질문")
"""


