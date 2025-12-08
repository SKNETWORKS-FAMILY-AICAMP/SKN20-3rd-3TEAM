import os
from dotenv import load_dotenv
import warnings
warnings.filterwarnings("ignore")

# LangChain 최신 버전 임포트
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.retrievers import BM25Retriever
from langchain_core.documents import Document
from typing import List

# EnsembleRetriever 직접 구현
class EnsembleRetriever:
    def __init__(self, retrievers: List, weights: List[float]):
        self.retrievers = retrievers
        self.weights = weights
    
    def invoke(self, query: str) -> List[Document]:
        """여러 retriever의 결과를 가중치 기반으로 결합"""
        all_docs = []
        doc_scores = {}
        
        for retriever, weight in zip(self.retrievers, self.weights):
            docs = retriever.invoke(query)
            
            # 각 문서에 가중치 적용
            for i, doc in enumerate(docs):
                doc_id = hash(doc.page_content)
                # 순위 기반 스코어 (상위일수록 높은 점수)
                score = weight * (len(docs) - i) / len(docs)
                
                if doc_id in doc_scores:
                    doc_scores[doc_id]['score'] += score
                else:
                    doc_scores[doc_id] = {'doc': doc, 'score': score}
        
        # 스코어 기준으로 정렬
        sorted_docs = sorted(doc_scores.values(), key=lambda x: x['score'], reverse=True)
        return [item['doc'] for item in sorted_docs]


load_dotenv()

if not os.environ.get('OPENAI_API_KEY'):
    raise ValueError('.env 확인하세요. key가 없습니다')

'''
벡터 DB 불러오기
'''
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

# 벡터스토어 로드
vectorstore = Chroma(
    persist_directory="./ChromaDB",
    collection_name="pet_health_qa_system",
    embedding_function=embeddings
)
print("벡터스토어가 성공적으로 로드되었습니다!")

# 컬렉션 정보 확인
collection = vectorstore._collection
print(f"총 문서 수: {collection.count()}")


# RAG 프롬프트
prompt = ChatPromptTemplate.from_messages([
    ("system", """
당신은 반려견 질병·증상에 대해 수의학 정보를 제공하는 AI 어시스턴트입니다. 
당신의 답변은 반드시 제공된 문맥(Context)만을 기반으로 해야 합니다.
문맥에 없는 정보는 절대로 추측하거나 생성하지 마세요.

[사용 가능한 정보 유형]
- medical_data: 수의학 서적 또는 논문
- qa_data: 보호자-수의사 상담 기록 (생애주기 / 과 / 질병 태그 포함)

[할루시네이션 방지 규칙]
1. 문맥에 없는 정보는 사용하지 마세요.
2. 관련 정보가 없다면 "해당 질문과 관련된 문서를 찾지 못했습니다."라고 답변하세요.
3. 여러 문서 제공시, 실제로 답변에 사용한 문서만 출처 명시하세요.
4. **질문에 합당한 답변만 제공하세요. 거짓 정보나 불필요한 정보는 제외하세요.**

[응답 규칙]
- 보호자가 작성한 반려견 상태를 2~3문장으로 요약한다.
- 문맥에서 확인된 가능한 원인을 구체적으로 설명한다. 
  (문맥에 없다면 "문서에 해당 정보가 없습니다"라고 쓴다)
- 집에서 가능한 안전한 관리 방법 2~3개 제안한다. 
  (문맥에 없다면 제안하지 않는다)
- 언제 병원에 가야 하는지, 어떤 증상이 응급인지 문서 기반으로 설명한다.
- 마지막 줄에 반드시 출처를 명시한다:
  • 서적 출처: 책 제목 / 저자 / 출판사
  • QA 출처: 생애주기 / 과 / 질병

[전체 톤]
- 공손한 존댓말
- 보호자를 안심시키되, 필요한 부분은 명확하게 안내하는 수의사 상담 톤

[출력 형식]
-상태 요약:
-가능한 원인:
-집에서 관리 방법:
-병원 방문 시기:
-출처(참고한 모든 문서)
"""),
    ("human", """
문맥: {context}

사용자 질문: {question}
""")
])


# 문서 포맷팅 함수
def format_docs(docs):
    if not docs:
        return "관련 문서를 찾지 못했습니다."
    
    formatted_docs = []
    for doc in docs:
        metadata = doc.metadata
        
        # 데이터 유형에 따라 출처 정보 구성
        if metadata.get("source_type") == "qa_data":
            source_info = f"상담기록 - {metadata.get('lifeCycle', '')}/{metadata.get('department', '')}/{metadata.get('disease', '')}"
        else:
            # 수의학 서적의 경우
            source_info = f"서적 - {metadata.get('title', '')}"
            if metadata.get('author'):
                source_info += f" (저자: {metadata['author']})"
            if metadata.get('page'):
                source_info += f" p.{metadata['page']+1}"
        
        formatted_doc = f"""<document>
<content>{doc.page_content}</content>
<source_info>{source_info}</source_info>
<data_type>{metadata.get('source_type', 'unknown')}</data_type>
</document>"""
        
        formatted_docs.append(formatted_doc)
    
    return "\n\n".join(formatted_docs)


# 1단계: Threshold 기반 Retriever
def threshold_retriever(query, threshold=0.35, k=10):
    """
    유사도 임계값을 사용하는 retriever
    
    Args:
        query: 검색 쿼리
        threshold: 최소 유사도 임계값 (0~1, 낮을수록 더 유사)
        k: 검색할 최대 문서 수
    
    Returns:
        임계값을 넘는 관련 문서 리스트
    """
    results = vectorstore.similarity_search_with_score(query, k=k)
    
    # 임계값 이하의 문서만 필터링 (거리가 작을수록 유사도 높음)
    filtered_docs = [doc for doc, score in results if score <= threshold]
    
    print(f"[1단계 Threshold] 검색된 문서: {len(results)}개 중 {len(filtered_docs)}개가 임계값({threshold}) 통과")
    if results:
        print(f"  유사도 범위: {results[0][1]:.3f} ~ {results[-1][1]:.3f}")
    
    return filtered_docs


# 2단계: MMR 기반 Retriever
def mmr_retriever(query, threshold=0.35, k=10, fetch_k=20, lambda_mult=0.5):
    """
    MMR(Maximal Marginal Relevance)을 사용하는 retriever
    유사도가 높으면서도 다양성을 고려한 문서 검색
    
    Args:
        query: 검색 쿼리
        threshold: 최소 유사도 임계값
        k: 최종 반환할 문서 수
        fetch_k: MMR 계산을 위해 초기에 가져올 문서 수
        lambda_mult: 유사도와 다양성의 균형 (0~1)
                    1에 가까울수록 유사도 우선
                    0에 가까울수록 다양성 우선
    
    Returns:
        MMR로 선택된 관련 문서 리스트
    """
    # MMR 검색 수행
    mmr_docs = vectorstore.max_marginal_relevance_search(
        query, 
        k=k,
        fetch_k=fetch_k,
        lambda_mult=lambda_mult
    )
    
    # 임계값 필터링을 위해 유사도 점수 확인
    # MMR 결과에 대해 다시 유사도 계산
    filtered_docs = []
    for doc in mmr_docs:
        # 각 문서의 유사도 점수 계산
        score_results = vectorstore.similarity_search_with_score(doc.page_content, k=1)
        if score_results and score_results[0][1] <= threshold:
            filtered_docs.append(doc)
    
    print(f"[2단계 MMR] fetch_k={fetch_k}개 중 k={k}개 선택 → 임계값 필터링 후 {len(filtered_docs)}개")
    print(f"  lambda_mult={lambda_mult} (유사도 vs 다양성 균형)")
    
    return filtered_docs


# 3단계: Ensemble Retriever (벡터 + BM25)
def ensemble_retriever(query, threshold=0.35, k=10, vector_weight=0.5, bm25_weight=0.5):
    """
    Ensemble Retriever: 벡터 검색 + BM25 키워드 검색 결합
    
    Args:
        query: 검색 쿼리
        threshold: 유사도 임계값
        k: 최종 반환할 문서 수
        vector_weight: 벡터 검색 가중치 (0~1)
        bm25_weight: BM25 검색 가중치 (0~1)
    
    Returns:
        Ensemble로 선택된 관련 문서 리스트
    """
    print(f"[3단계 Ensemble] 벡터({vector_weight}) + BM25({bm25_weight}) 결합")
    
    # 벡터스토어에서 모든 문서 가져오기 (BM25용)
    # 효율성을 위해 상위 1000개만 사용
    all_docs_results = vectorstore.similarity_search("", k=1000)
    
    if not all_docs_results:
        print("  ⚠️ 문서를 가져올 수 없습니다.")
        return []
    
    # BM25 Retriever 생성
    bm25_retriever = BM25Retriever.from_documents(all_docs_results)
    bm25_retriever.k = k
    
    # 벡터 Retriever 생성
    vector_retriever = vectorstore.as_retriever(
        search_kwargs={"k": k}
    )
    
    # Ensemble Retriever 생성 (직접 구현한 클래스 사용)
    ensemble = EnsembleRetriever(
        retrievers=[vector_retriever, bm25_retriever],
        weights=[vector_weight, bm25_weight]
    )
    
    # Ensemble 검색 수행
    ensemble_docs = ensemble.invoke(query)
    
    print(f"  Ensemble 검색 결과: {len(ensemble_docs)}개 문서")
    
    # 임계값 필터링
    filtered_docs = []
    for doc in ensemble_docs:
        score_results = vectorstore.similarity_search_with_score(doc.page_content, k=1)
        if score_results and score_results[0][1] <= threshold:
            filtered_docs.append(doc)
    
    print(f"  임계값 필터링 후: {len(filtered_docs)}개 문서")
    
    # 중복 제거 (같은 content를 가진 문서)
    unique_docs = []
    seen_contents = set()
    for doc in filtered_docs:
        content_hash = hash(doc.page_content)
        if content_hash not in seen_contents:
            seen_contents.add(content_hash)
            unique_docs.append(doc)
    
    print(f"  중복 제거 후: {len(unique_docs)}개 문서")
    
    return unique_docs[:k]  # k개만 반환


# 통합 검색 함수
def multi_stage_retriever(query, stage=1, threshold=0.35, k=10):
    """
    다단계 검색 전략
    
    Args:
        query: 검색 쿼리
        stage: 검색 단계 (1: Threshold, 2: MMR, 3: Ensemble)
        threshold: 유사도 임계값
        k: 반환할 문서 수
    
    Returns:
        검색된 문서 리스트
    """
    print(f"\n{'='*60}")
    print(f"검색 쿼리: {query}")
    print(f"검색 단계: {stage}단계")
    print(f"{'='*60}")
    
    if stage == 1:
        # 1단계: Threshold만 사용
        docs = threshold_retriever(query, threshold=threshold, k=k)
    elif stage == 2:
        # 2단계: MMR 검색
        docs = mmr_retriever(
            query, 
            threshold=threshold, 
            k=k, 
            fetch_k=k*2,
            lambda_mult=0.5
        )
    elif stage == 3:
        # 3단계: Ensemble (벡터 + BM25)
        docs = ensemble_retriever(
            query,
            threshold=threshold,
            k=k,
            vector_weight=0.5,
            bm25_weight=0.5
        )
    else:
        raise ValueError("stage는 1, 2, 3 중 하나여야 합니다.")
    
    return docs


# LLM 및 체인 설정
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
rag_chain = prompt | llm | StrOutputParser()


# 예시 질문으로 테스트
query_list = [
    # "우리 강아지가 갑자기 구토를 시작했어요. 며칠 전부터 식욕도 없고 기운이 없어 보여서 걱정입니다. 어떤 원인일 수 있을까요? 집에서 어떻게 돌봐줘야 하나요?",
    # "바닷속에서 가장 유명한 강아지는 누구인가요?",
    # "우리 강아지가 노견인데 기침을하다가 오늘 기절했어 의심되는 질환이 뭔지 알려주고, 위험도가 어느정도인가요?",
    # "나 배고파",
    # "강아지가 기절함",
    '강아지의 심장 사상충 감염은 어떻게 진단하나요?',
    '반려견의 슬개골 탈구 4단계는 구체적으로 어떤 상태를 의미하며, 치료 방법은 무엇인가요?',
    '어린 고양이(자묘)의 예방 접종 스케줄과 성묘의 치과 검진 주기를 모두 설명해 주세요.',
    '강아지의 알레르기 피부염과 아토피 피부염의 주요 차이점은 무엇이며, 보호자 입장에서 가장 먼저 시도할 수 있는 관리는 무엇인가요?',
    '중성화 수술 후 반려견의 식단 관리는 어떻게 해야 하며, 권장되는 운동량은 어느 정도인가요?',
    '우리 집 늙은 개가 자꾸 물을 많이 마시고 오줌을 자주 누는 현상이 심해지고 있는데, 의심해 볼 수 있는 내과 질환은 무엇인가요?',
    '고양이의 감기에 걸리면 사람처럼 항생제를 먹여야만 낫나요?',
    '동물 병원에서 안과 질환 진료 시 사용하는 기본적인 검사 장비들에 대해 알려주세요.',
    '한국에 없는 특이한 외래종 앵무새의 먹이는 무엇인가요?',
    '강아지가 췌장염에 걸렸을 때의 초기 증상부터 입원 후 치료 과정, 그리고 퇴원 후 보호자가 관리해야 할 식이요법까지 상세하게 알려주세요.',


]



# 3단계 비교 테스트 함수
def compare_all_stages(query, threshold=0.35, k=5):
    """
    1단계, 2단계, 3단계 검색을 모두 비교
    """
    print("\n" + "🔍"*40)
    print(f"질문: {query}")
    print("🔍"*40)
    
    stages = [
        (1, "Threshold Only"),
        (2, "MMR (다양성)"),
        (3, "Ensemble (벡터+BM25)")
    ]
    
    for stage_num, stage_name in stages:
        print(f"\n{'='*80}")
        print(f"[{stage_num}단계: {stage_name}]")
        print(f"{'='*80}")
        
        # 검색 수행
        docs = multi_stage_retriever(query, stage=stage_num, threshold=threshold, k=k)
        
        # 검색된 문서 제목 출력
        print("\n검색된 문서:")
        for i, doc in enumerate(docs, 1):
            metadata = doc.metadata
            title = metadata.get('disease', '') or metadata.get('title', 'Unknown')
            source_type = metadata.get('source_type', 'unknown')
            print(f"  {i}. [{source_type}] {title}")
        
        # RAG 답변 생성
        context = format_docs(docs)
        answer = rag_chain.invoke({"context": context, "question": query})
        
        print(f"\n📝 답변:\n{answer}\n")
    
    print("\n" + "="*80)
    print("비교 완료!")
    print("="*80)


# 테스트 실행 예시
if __name__ == "__main__":
    # 특정 질문에 대해 3단계 모두 비교
    if __name__ == "__main__":
    # 기절 관련 문서가 실제로 있는지 확인
        test_results = vectorstore.similarity_search_with_score("기절", k=10)
        
        print("\n=== '기절' 검색 결과 ===")
        for i, (doc, score) in enumerate(test_results, 1):
            title = doc.metadata.get('disease', '') or doc.metadata.get('title', 'Unknown')
            print(f"{i}. [{score:.3f}] {title}")
            print(f"   내용: {doc.page_content[:100]}...")
    test_query = "강아지가 기절함"
    compare_all_stages(test_query, threshold=0.35, k=5)
    
    # 또는 개별 단계 테스트
    print("\n=== 3단계 Ensemble 테스트 ===")
    for q in query_list:
        docs = multi_stage_retriever(q, stage=3, threshold=0.35, k=5)
        context = format_docs(docs)
        generation = rag_chain.invoke({"context": context, "question": q})
        print(f"\n질문: {q}")
        print(f"답변:\n{generation}\n")
        print("="*80)