"""
RAG Pipeline 모듈
LangGraph 기반 CRAG (Corrective RAG) 패턴 구현
문서 관련성 평가 후, 없으면 웹 검색으로 폴백
상세한 디버깅 로그 포함
"""
from typing import List, Dict, Any, Literal
from typing_extensions import TypedDict
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_community.retrievers import TavilySearchAPIRetriever
from pydantic import BaseModel, Field
from langgraph.graph import StateGraph, START, END
import os
import warnings
warnings.filterwarnings("ignore")


# ==================== State 정의 ====================
class CRAGState(TypedDict):
    """CRAG 파이프라인의 상태"""
    question: str
    original_question: str  # 최적화 전 원본 질문
    documents: List[Document]
    document_scores: List[float]  # similarity scores
    filtered_documents: List[Document]
    relevance_scores: List[float]  # LLM 평가 점수
    web_search_needed: str
    web_search_reason: str  # 웹 검색 실행 이유
    context: str
    answer: str
    grade_results: List[str]
    sources: List[Dict[str, Any]]
    answer_quality: str  # "pass" 또는 "fail"
    answer_quality_reason: str  # 평가 사유
    rewrite_count: int  # Rewrite 시도 횟수


class GradeDocuments(BaseModel):
    """문서 관련성 평가 결과"""
    binary_score: str = Field(
        description="문서가 질문과 관련이 있으면 'yes', 없으면 'no'"
    )


class LangGraphRAGPipeline:
    """
    LangGraph 기반 CRAG (Corrective RAG) 파이프라인
    
    문서 관련성을 평가하고, 관련 문서가 없으면 웹 검색으로 폴백하는 고급 RAG 시스템
    디버깅 로그를 상세히 표시합니다.
    """
    
    def __init__(
        self,
        retriever: BaseRetriever,
        llm_model: str = "gpt-4o-mini",
        temperature: float = 0.0,
        debug: bool = True
    ):
        """
        Args:
            retriever: 문서 검색기
            llm_model: LLM 모델 이름
            temperature: LLM temperature
            debug: 디버깅 로그 출력 여부
        """
        self.retriever = retriever
        self.llm = ChatOpenAI(model=llm_model, temperature=temperature)
        self.grader_llm = ChatOpenAI(model=llm_model, temperature=0)
        self.debug = debug
        
        # 웹 검색 설정
        try:
            self.web_search = TavilySearchAPIRetriever(k=3)
            self.web_search_available = True
            if self.debug:
                print("✅ Tavily 웹 검색 API 초기화 성공")
        except Exception as e:
            print(f"⚠️ 경고: 웹 검색 API 초기화 실패 - {str(e)}")
            self.web_search_available = False
        
        # 구조화된 grader 설정
        self.document_grader = self._setup_grader()
        
        # LangGraph 앱 구축
        self.app = self._build_graph()
    
    def _setup_grader(self):
        """문서 관련성 평가기 설정"""
        structured_grader = self.grader_llm.with_structured_output(GradeDocuments)
        
        grade_prompt = ChatPromptTemplate.from_messages([
            ("system", """당신은 검색된 문서가 사용자의 질문에 답변하는데 관련이 있는지 평가하는 전문가입니다.

평가 기준:
- 문서가 질문의 키워드, 개념, 또는 주제와 직접적으로 관련되어 있으면 'yes'
- 문서가 질문의 배경, 맥락, 또는 관련 개념을 다루면 'yes'
- 문서가 질문과 명확한 연관성이 없으면 'no'

주의: 약간의 연관성만 있어도 'yes'를 반환하세요."""),
            ("human", """질문: {question}

문서 내용:
{document}

관련성 판정 (yes/no):""")
        ])
        
        return grade_prompt | structured_grader
    
    def _setup_query_rewriter(self):
        """웹 검색용 쿼리 최적화 LLM 설정"""
        rewrite_prompt = ChatPromptTemplate.from_messages([
            ("system", """당신은 사용자의 질문을 웹 검색에 최적화된 키워드로 변환하는 전문가입니다.

원칙:
1. 질문의 핵심 키워드를 추출하세요.
2. 검색에 불필요한 존댓말, 인사말 제거하세요.
3. 검색 엔진이 잘 이해할 수 있는 간결한 형태로 변환하세요.
4. 중요한 지역명, 카테고리명을 강조하세요.
5. 한국어 또는 영문 키워드 조합으로 작성하세요.

예시:
- 입력: "서울시 여의도 공원 근처에 있는 동물병원을 알려주세요"
- 출력: "여의도 공원 동물병원"

- 입력: "강아지 피부 질환에 대해 알고 싶어요"
- 출력: "강아지 피부질환 증상 치료"

최적화된 검색 쿼리만 반환하세요 (설명 없이)."""),
            ("human", "{question}")
        ])
        
        return rewrite_prompt | self.llm | StrOutputParser()
    
    def _build_graph(self):
        """LangGraph 상태 그래프 구축 (평가 및 Rewrite 루프 포함)"""
        workflow = StateGraph(CRAGState)
        
        # 노드들 정의
        workflow.add_node("retrieve", self._retrieve_node)
        workflow.add_node("grade_documents", self._grade_documents_node)
        workflow.add_node("query_rewrite", self._query_rewrite_node)
        workflow.add_node("web_search", self._web_search_node)
        workflow.add_node("generate", self._generate_node)
        workflow.add_node("evaluate_answer", self._evaluate_answer_node)  # 평가 노드 추가
        
        # 엣지 설정
        workflow.add_edge(START, "retrieve")
        workflow.add_edge("retrieve", "grade_documents")
        workflow.add_conditional_edges(
            "grade_documents",
            self._decide_to_generate,
            {
                "generate": "generate",
                "web_search": "query_rewrite"
            }
        )
        workflow.add_edge("query_rewrite", "web_search")
        workflow.add_edge("web_search", "generate")
        workflow.add_edge("generate", "evaluate_answer")  # 생성 후 평가
        
        # 평가 결과에 따른 조건부 라우팅
        workflow.add_conditional_edges(
            "evaluate_answer",
            self._decide_after_evaluation,
            {
                "end": END,
                "rewrite": "query_rewrite"  # Fail 시 쿼리 재작성
            }
        )
        
        return workflow.compile()
    
    def _retrieve_node(self, state: CRAGState) -> dict:
        """내부 문서 검색 노드 (similarity score 포함, top_k=5)"""
        question = state['question']
        
        if self.debug:
            print("\n" + "="*80)
            print("📍 [1/5] RETRIEVE NODE - top_k=5 벡터DB 검색")
            print("="*80)
            print(f"❓ 질문: {question}\n")
        
        # retriever가 retrieve_with_scores 메서드를 지원하는지 확인
        if hasattr(self.retriever, 'retrieve_with_scores'):
            doc_scores = self.retriever.retrieve_with_scores(question)
            documents = [doc for doc, _ in doc_scores]
            scores = [score for _, score in doc_scores]
        elif hasattr(self.retriever, 'vectorstore'):
            # ThresholdRetriever의 vectorstore에 직접 접근
            results = self.retriever.vectorstore.similarity_search_with_score(question, k=5)
            documents = []
            scores = []
            for doc, distance in results:
                # 거리를 유사도 점수로 변환
                similarity_score = 1.0 - distance if distance <= 1.0 else max(0.0, 1.0 - distance)
                doc.metadata['similarity_score'] = similarity_score
                documents.append(doc)
                scores.append(similarity_score)
        else:
            # 기본 retriever 사용
            documents = self.retriever.invoke(question)
            scores = [0.0] * len(documents)
            if self.debug:
                print("⚠️ 경고: Retriever가 similarity score를 제공하지 않습니다.")
        
        if self.debug:
            print(f"✅ 검색 완료: {len(documents)}개 문서 반환 (top_k=5)")
            print(f"\n📋 검색된 문서 리스트 (similarity 기반 상위 5개):")
            for i, (doc, score) in enumerate(zip(documents, scores), 1):
                source = doc.metadata.get('file_name', 'unknown')
                dept = doc.metadata.get('department', '')
                dept_str = f" | {dept}" if dept else ""
                content_preview = doc.page_content[:70].replace('\n', ' ')
                print(f"   [{i}] 📄 {source}{dept_str}")
                print(f"       점수: {score:.4f}")
                print(f"       내용: {content_preview}...\n")
        
        return {
            'documents': documents,
            'document_scores': scores,
            'question': question,
            'original_question': question  # 원본 질문 저장
        }
    
    def _grade_documents_node(self, state: CRAGState) -> dict:
        """문서 관련성 평가 노드 (Yes/No 기준)"""
        question = state['question']
        documents = state['documents']
        filtered_docs = []
        grade_results = []
        
        if self.debug:
            print("\n" + "="*80)
            print("📍 [2/5] GRADE DOCUMENTS NODE - LLM 관련성 평가 (0.5 threshold)")
            print("="*80)
            print(f"❓ 질문: {question}")
            print(f"📊 평가할 문서 수: {len(documents)}개\n")
        
        for idx, doc in enumerate(documents, 1):
            try:
                source = doc.metadata.get('file_name', 'unknown')
                content_preview = doc.page_content[:60].replace('\n', ' ')
                similarity_score = doc.metadata.get('similarity_score', 0.0)
                
                if self.debug:
                    print(f"   📄 [{idx}] {source} (similarity: {similarity_score:.4f})")
                    print(f"       내용: {content_preview}...")
                
                # LLM으로 관련성 평가 (Yes/No)
                score_result = self.document_grader.invoke({
                    'question': question,
                    'document': doc.page_content
                })
                grade = score_result.binary_score.lower().strip()
                
                # yes인 문서만 필터링
                if grade == 'yes':
                    filtered_docs.append(doc)
                    grade_results.append("YES")
                    if self.debug:
                        print(f"       ✅ 관련있음 (yes)")
                else:
                    grade_results.append("NO")
                    if self.debug:
                        print(f"       ❌ 관련없음 (no)")
            except Exception as e:
                print(f"       ⚠️ 평가 오류: {str(e)}")
                grade_results.append("ERROR")
        
        # 최종 결과 통계
        relevant_docs_count = len(filtered_docs)
        
        if self.debug:
            print(f"\n📊 평가 결과 요약:")
            print(f"   ✅ 관련있음: {sum(1 for r in grade_results if r == 'YES')}개")
            print(f"   ❌ 관련없음: {sum(1 for r in grade_results if r == 'NO')}개")
            print(f"   🎯 최종 관련 문서 수: {relevant_docs_count}개")
        
        # Fallback 이유 설정
        web_search_reason = ""
        if relevant_docs_count == 0:
            web_search_reason = "관련 있는 문서 0개"
        
        return {
            "filtered_documents": filtered_docs,
            "relevance_scores": [],  # yes/no 방식이므로 점수 없음
            "web_search_needed": "Yes" if relevant_docs_count == 0 else "No",
            "web_search_reason": web_search_reason,
            "grade_results": grade_results
        }
    
    def _decide_to_generate(self, state: CRAGState) -> Literal["generate", "web_search"]:
        """
        다음 단계 결정 (생성 또는 웹 검색)
        
        개선된 로직 (Threshold 기반):
        - avg_relevance_score >= THRESHOLD → GENERATE (내부 문서 답변)
        - avg_relevance_score < THRESHOLD → WEB_SEARCH (웹 검색)
        """
        filtered_docs = state.get("filtered_documents", [])
        document_scores = state.get("document_scores", [])
        RELEVANCE_THRESHOLD = 0.5  # 관련성 점수 기준
        MIN_DOCS_THRESHOLD = 1  # 최소 문서 수
        
        if self.debug:
            print("\n" + "="*80)
            print("📍 [3/5] DECISION NODE - 다음 루트 결정 (Threshold 기반)")
            print("="*80)
            print(f"📊 관련 문서 수: {len(filtered_docs)}개")
            if document_scores:
                avg_score = sum(document_scores) / len(document_scores)
                print(f"📊 Similarity Score 평균: {avg_score:.4f}")
        
        relevant_docs_count = len(filtered_docs)
        
        if self.debug:
            print(f"\n📋 판정 기준:")
            print(f"   - 관련 문서 최소 개수: {MIN_DOCS_THRESHOLD}개")
            print(f"   - 관련성 점수 기준(Threshold): {RELEVANCE_THRESHOLD}")
            print(f"   - 웹 검색 API 가용: {self.web_search_available}")
        
        # 개선된 조건 판정
        # 1. 관련 문서가 최소 개수 이상이면서
        # 2. 평균 유사도 점수가 Threshold 이상인 경우만 내부 문서로 답변
        if relevant_docs_count >= MIN_DOCS_THRESHOLD:
            # 점수 기반 평가
            if document_scores:
                avg_score = sum(document_scores) / len(document_scores)
                
                # 높은 신뢰도 → 내부 문서 사용
                if avg_score >= RELEVANCE_THRESHOLD:
                    if self.debug:
                        print(f"\n✅ 결정: GENERATE 루트")
                        print(f"   → 이유: 평균 점수 {avg_score:.4f} >= {RELEVANCE_THRESHOLD}")
                        print(f"   → 내부 문서 기반 고품질 답변 생성")
                    return "generate"
                # 낮은 신뢰도 → 웹 검색으로 보완
                else:
                    if self.debug:
                        print(f"\n🌐 결정: WEB_SEARCH 루트")
                        print(f"   → 이유: 평균 점수 {avg_score:.4f} < {RELEVANCE_THRESHOLD}")
                        print(f"   → 웹 검색으로 더 나은 정보 획득")
                    return "web_search" if self.web_search_available else "generate"
            else:
                # 점수 정보가 없으면 문서 개수로 판정
                if self.debug:
                    print(f"\n✅ 결정: GENERATE 루트 (점수 정보 없음)")
                return "generate"
        
        # 관련 문서가 없는 경우 웹 검색
        else:
            if self.web_search_available:
                if self.debug:
                    print(f"\n🌐 결정: WEB_SEARCH 루트")
                    print(f"   → 이유: 관련 문서 부족 (0개)")
                    print(f"   → 웹에서 정보 검색")
                return "web_search"
            else:
                # 웹 검색 API 불가능한 경우 내부 문서로 진행
                if self.debug:
                    print(f"\n⚠️ 결정: GENERATE 루트 (웹 검색 API 불가)")
                    print(f"   → 웹 검색 API 불가능 → 내부 문서로 진행")
                return "generate"
    
    def _query_rewrite_node(self, state: CRAGState) -> dict:
        """
        웹 검색용 쿼리 최적화 노드
        Fail 상황에서는 더 개선된 쿼리 작성
        """
        question = state["question"]
        rewrite_count = state.get("rewrite_count", 0)
        is_rewrite = rewrite_count > 0  # 재작성인지 처음인지 확인
        
        if self.debug:
            if is_rewrite:
                print("\n" + "="*80)
                print(f"📍 QUERY REWRITE NODE (재시도 {rewrite_count}) - 쿼리 개선")
                print("="*80)
            else:
                print("\n" + "="*80)
                print("📍 [3-1/5] QUERY REWRITE NODE - 웹 검색 쿼리 최적화")
                print("="*80)
            print(f"❓ 원본 질문: {question}\n")
        
        try:
            # 재작성인 경우 더 강화된 프롬프트 사용
            if is_rewrite:
                rewrite_prompt = ChatPromptTemplate.from_messages([
                    ("system", """이전 답변이 만족스럽지 못했습니다.
더 나은 답변을 얻기 위해 검색 쿼리를 더 구체적으로 개선하세요.

개선 방법:
1. 핵심 키워드 강조
2. 추가 맥락 포함
3. 동의어나 관련 용어 추가
4. 구체적인 예시 또는 세부사항 포함"""),
                    ("human", "{question}")
                ])
            else:
                query_rewriter = self._setup_query_rewriter()
                optimized_query = query_rewriter.invoke({"question": question}).strip()
                
                if self.debug:
                    print(f"🔍 최적화된 검색 쿼리: {optimized_query}")
                    print(f"   → 이 쿼리로 웹 검색 수행합니다\n")
                
                return {
                    "question": optimized_query,
                    "rewrite_count": rewrite_count + 1
                }
            
            # 재작성용 LLM
            rewriter = self.llm.with_structured_output(
                type("QueryRewrite", (), {"query": str})
            )
            
            improved_question = rewrite_prompt | self.llm | StrOutputParser()
            optimized_query = improved_question.invoke({"question": question}).strip()
            
            if self.debug:
                print(f"🔄 개선된 검색 쿼리: {optimized_query}\n")
        
        except Exception as e:
            if self.debug:
                print(f"⚠️ 쿼리 최적화 실패: {str(e)}")
                print(f"   → 원본 질문으로 검색 진행")
            optimized_query = question
        
        return {
            "question": optimized_query,
            "rewrite_count": rewrite_count + 1
        }
    
    def _web_search_node(self, state: CRAGState) -> dict:
        """웹 검색 노드 (최적화된 쿼리 사용, 웹 검색 결과를 우선순위 높게 배치)"""
        question = state["question"]  # 이미 최적화된 쿼리
        original_question = state.get("original_question", question)
        filtered_docs = state.get("filtered_documents", [])
        
        if self.debug:
            print("\n" + "="*80)
            print("📍 [3-2/5] WEB SEARCH NODE - Tavily API로 웹 검색")
            print("="*80)
            print(f"❓ 최적화된 검색 쿼리: {question}")
            print(f"📊 현재 보유 문서: {len(filtered_docs)}개\n")
        
        web_results = []
        try:
            if self.debug:
                print("🔍 Tavily API로 웹 검색 중...")
            
            # Tavily API로 웹 검색 수행 (최적화된 쿼리 사용)
            web_results = self.web_search.invoke(question)
            
            if self.debug:
                print(f"✅ 웹 검색 완료: {len(web_results)}개 결과")
            
            # 웹 검색 결과를 Document로 변환하고 메타데이터 설정
            web_docs = []
            for i, doc in enumerate(web_results, 1):
                if isinstance(doc, Document):
                    # 웹 검색 결과임을 명시
                    doc.metadata['source'] = doc.metadata.get('source', 'web')
                    doc.metadata['source_type'] = 'web'
                    doc.metadata['search_query'] = question  # 사용된 검색 쿼리 기록
                    web_docs.append(doc)
                    if self.debug:
                        source = doc.metadata.get('source', 'web')
                        content_preview = doc.page_content[:70].replace('\n', ' ')
                        print(f"   [{i}] 🌐 {source}")
                        print(f"       내용: {content_preview}...")
            
            # 웹 검색 결과를 우선순위 높게 배치 (앞에 배치)
            final_docs = web_docs + filtered_docs
            
            if self.debug:
                print(f"\n✅ 웹 검색 결과 통합 완료")
                print(f"📊 최종 문서 수: {len(final_docs)}개 (웹: {len(web_docs)}개, 내부: {len(filtered_docs)}개)")
                print(f"   → 웹 검색 결과가 내부 문서보다 우선순위 높게 배치됨")
        except Exception as e:
            if self.debug:
                print(f"❌ 웹 검색 실패: {str(e)}")
                print("   → 기존 문서로 진행합니다")
            final_docs = filtered_docs
        
        return {
            "filtered_documents": final_docs
        }
    
    def _generate_node(self, state: CRAGState) -> dict:
        """답변 생성 노드 - 관련 문서 여부에 따라 처리"""
        question = state["question"]
        filtered_documents = state['filtered_documents']
        
        if self.debug:
            print("\n" + "="*80)
            print("📍 [4/5] GENERATE NODE - 최종 답변 생성")
            print("="*80)
            print(f"❓ 질문: {question}")
            print(f"📄 사용할 문서: {len(filtered_documents)}개\n")
            
            # 문서 출처 정보 표시
            if filtered_documents:
                print(f"📋 사용 문서 리스트:")
                for i, doc in enumerate(filtered_documents[:5], 1):
                    source = doc.metadata.get('file_name', doc.metadata.get('source', 'unknown'))
                    source_type = doc.metadata.get('source_type', 'internal')
                    type_marker = '🌐' if source_type == 'web' else '📄'
                    dept = doc.metadata.get('department', '')
                    dept_str = f" | {dept}" if dept else ""
                    print(f"   [{i}] {type_marker} {source}{dept_str}")
                if len(filtered_documents) > 5:
                    print(f"   ... 외 {len(filtered_documents) - 5}개")
                print()
        
        # 컨텍스트 구성
        context = self._format_docs(filtered_documents)
        
        if self.debug:
            print(f"📝 컨텍스트 크기: {len(context):,} 문자")
        
        # 웹 검색 결과 포함 여부 확인
        has_web_search = any(doc.metadata.get('source_type') == 'web' for doc in filtered_documents)
        
        # 답변 생성 프롬프트 (웹 검색 결과 포함 시 더 유연하게)
        if has_web_search:
            system_prompt = """당신은 제공된 문서를 기반으로 질문에 답변하는 AI 어시스턴트입니다.

규칙:
1. 제공된 문서(문맥)에 있는 정보를 우선적으로 사용하여 답변하세요.
2. 웹 검색 결과를 포함합니다. 불완전한 정보라도 출처를 명시하고 조합하여 답변을 구성하세요.
3. 여러 출처의 정보를 통합할 때는 각 출처를 명확히 표기하세요 (예: "ABC 출처에 따르면...", "OOO 웹사이트에서는...").
4. 정보의 신뢰성이 낮거나 확인이 필요한 경우, 이를 명시하세요 (예: "해당 정보는 확인이 필요합니다").
5. 완전히 다른 주제의 정보는 추측하지 마세요.
6. 답변은 한국어로 명확하고 간결하게 작성하세요.
7. 가능하면 문서의 내용을 인용하여 답변하세요."""
        else:
            system_prompt = """당신은 제공된 문서를 기반으로 질문에 답변하는 AI 어시스턴트입니다.

규칙:
1. 반드시 제공된 문서(문맥)에 있는 정보만을 사용하여 답변하세요.
2. 문서에 없는 정보나 사실은 추측하지 마세요.
3. 문서에 정보가 충분하지 않으면, "제공된 문서에는 이 정보가 없습니다"라고 답변하세요.
4. 답변은 한국어로 명확하고 간결하게 작성하세요.
5. 가능하면 문서의 내용을 인용하여 답변하세요."""
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", """문맥(참고 문서):
{context}

질문: {question}

위 문맥을 바탕으로 질문에 답변하세요.""")
        ])
        
        if self.debug:
            print("🤖 LLM으로 답변 생성 중...")
        
        chain = prompt | self.llm | StrOutputParser()
        answer = chain.invoke({"context": context, "question": question})
        
        if self.debug:
            answer_preview = answer[:100].replace('\n', ' ')
            print(f"✅ 답변 생성 완료")
            print(f"   미리보기: {answer_preview}...\n")
        
        # 출처 정보 수집
        sources = []
        for doc in filtered_documents:
            source_type = doc.metadata.get('source_type', 'internal')
            sources.append({
                'file_name': doc.metadata.get('file_name', doc.metadata.get('source', 'unknown')),
                'source_path': doc.metadata.get('source_path', 'unknown'),
                'department': doc.metadata.get('department', 'unknown'),
                'title': doc.metadata.get('title', 'unknown'),
                'type': source_type
            })
        
        return {
            "context": context,
            "answer": answer,
            "sources": sources,
            "rewrite_count": state.get("rewrite_count", 0)  # Rewrite 카운트 유지
        }
    
    def _evaluate_answer_node(self, state: CRAGState) -> dict:
        """
        생성된 답변의 품질 평가 노드
        
        평가 기준:
        - 질문에 직접 답변했는가?
        - 정보가 충분한가?
        - 명확하고 이해하기 쉬운가?
        """
        question = state["question"]
        answer = state["answer"]
        
        if self.debug:
            print("\n" + "="*80)
            print("📍 [5/5] EVALUATE ANSWER NODE - 답변 품질 평가")
            print("="*80)
            print(f"❓ 질문: {question}")
            print(f"📝 답변: {answer[:150].replace(chr(10), ' ')}...\n")
        
        # 평가 프롬프트
        evaluation_prompt = ChatPromptTemplate.from_messages([
            ("system", """당신은 AI 답변의 품질을 평가하는 전문가입니다.
            
평가 기준:
1. 질문에 직접 답변했는가? (답변이 질문의 주요 내용을 다루고 있는가?)
2. 정보가 충분한가? (필요한 세부사항이 포함되어 있는가?)
3. 명확하고 이해하기 쉬운가? (논리적이고 구조화되어 있는가?)

답변을 평가하고 'PASS' 또는 'FAIL'로 판정하세요.
만약 FAIL이면 개선할 점을 간단히 기술하세요."""),
            ("human", """질문: {question}

답변: {answer}

평가 결과 (PASS/FAIL)와 이유를 제시하세요.""")
        ])
        
        # 구조화된 출력 설정
        class AnswerEvaluation(BaseModel):
            quality_score: str = Field(description="PASS 또는 FAIL")
            reason: str = Field(description="평가 사유")
        
        evaluator = self.grader_llm.with_structured_output(AnswerEvaluation)
        chain = evaluation_prompt | evaluator
        
        evaluation = chain.invoke({
            "question": question,
            "answer": answer
        })
        
        quality = evaluation.quality_score.upper()
        if "PASS" in quality:
            quality = "pass"
        else:
            quality = "fail"
        
        if self.debug:
            print(f"⭐ 평가 결과: {quality.upper()}")
            print(f"📌 평가 사유: {evaluation.reason}\n")
        
        return {
            "answer_quality": quality,
            "answer_quality_reason": evaluation.reason,
            "rewrite_count": state.get("rewrite_count", 0)
        }
    
    def _decide_after_evaluation(self, state: CRAGState) -> Literal["end", "rewrite"]:
        """
        평가 결과에 따라 최종 답변 또는 재작성 결정
        """
        quality = state.get("answer_quality", "fail")
        rewrite_count = state.get("rewrite_count", 0)
        max_rewrites = 2  # 최대 2회 재작성
        
        if self.debug:
            print(f"\n🔀 평가 결과 라우팅 - Quality: {quality}, Rewrites: {rewrite_count}/{max_rewrites}")
        
        # PASS 또는 최대 재작성 횟수 도달 시 종료
        if quality == "pass" or rewrite_count >= max_rewrites:
            return "end"
        else:
            return "rewrite"
    
    def _format_docs(self, docs: List[Document]) -> str:
        """검색된 문서들을 문자열로 포맷팅 (웹 검색 결과 구분)"""
        formatted = []
        for i, doc in enumerate(docs, 1):
            source = doc.metadata.get('file_name', doc.metadata.get('source', 'unknown'))
            department = doc.metadata.get('department', '')
            source_type = doc.metadata.get('source_type', 'internal')
            dept_str = f" ({department})" if department else ""
            
            # 웹 검색 결과인지 표시
            type_marker = "[웹 검색 결과]" if source_type == 'web' else "[내부 문서]"
            formatted.append(
                f"{type_marker} [문서 {i} - {source}{dept_str}]\n{doc.page_content}"
            )
        return "\n\n---\n\n".join(formatted) if formatted else "검색된 문서가 없습니다."
    
    def rag_pipeline(self, query: str) -> str:
        """
        RAG 파이프라인 실행
        
        Args:
            query: 사용자 질문
            
        Returns:
            답변 문자열
        """
        try:
            if self.debug:
                print("\n" + "🚀"*40)
                print("🚀 RAG 파이프라인 시작 🚀".center(80))
                print("🚀"*40)
            
            initial_state = {
                "question": query,
                "original_question": query,
                "documents": [],
                "document_scores": [],
                "filtered_documents": [],
                "relevance_scores": [],
                "web_search_needed": "No",
                "web_search_reason": "",
                "context": "",
                "answer": "",
                "grade_results": [],
                "sources": []
            }
            
            result = self.app.invoke(initial_state)
            
            if self.debug:
                print("\n" + "="*80)
                print("✅ 파이프라인 완료")
                print("="*80)
                # 최종 Debug Log 출력
                print("\n📊 최종 Debug Log:")
                doc_scores = result.get('document_scores', [])
                if doc_scores:
                    print(f"   - Top-K 문서 Similarity Score: {[f'{s:.4f}' for s in doc_scores]}")
                print(f"   - Threshold 필터 이후 남은 문서 수: {len(result.get('filtered_documents', []))}개")
                relevance_scores = result.get('relevance_scores', [])
                if relevance_scores:
                    avg_relevance = sum(relevance_scores) / len(relevance_scores)
                    print(f"   - 최종 Relevance Score 평균: {avg_relevance:.4f}")
                print(f"   - Fallback 여부: {'웹 검색 실행' if result.get('web_search_needed') == 'Yes' else '내부 문서 사용'}")
                if result.get('web_search_reason'):
                    print(f"   - 웹 검색 실행 이유: {result.get('web_search_reason')}")
                print()
            
            return result.get('answer', '답변을 생성할 수 없습니다.')
        except Exception as e:
            error_msg = f"오류가 발생했습니다: {str(e)}"
            if self.debug:
                print(f"\n❌ {error_msg}")
            return error_msg
    
    def rag_pipeline_with_sources(self, query: str) -> Dict[str, Any]:
        """
        RAG 파이프라인 실행 (출처 정보 포함)
        
        Args:
            query: 사용자 질문
            
        Returns:
            답변과 출처 정보를 포함한 딕셔너리
        """
        try:
            if self.debug:
                print("\n" + "🚀"*40)
                print("🚀 RAG 파이프라인 시작 🚀".center(80))
                print("🚀"*40)
            
            initial_state = {
                "question": query,
                "original_question": query,
                "documents": [],
                "document_scores": [],
                "filtered_documents": [],
                "relevance_scores": [],
                "web_search_needed": "No",
                "web_search_reason": "",
                "context": "",
                "answer": "",
                "grade_results": [],
                "sources": [],
                "answer_quality": "fail",  # 평가 초기값
                "answer_quality_reason": "",
                "rewrite_count": 0  # Rewrite 카운트
            }
            
            result = self.app.invoke(initial_state)
            
            if self.debug:
                print("\n" + "="*80)
                print("✅ RAG 파이프라인 완료")
                print("="*80)
                
                # 최종 결과 요약
                print("\n📊 최종 실행 결과:")
                
                # 1. Top-K 검색 결과
                doc_scores = result.get('document_scores', [])
                print(f"\n[1] Top-K=5 검색 결과:")
                if doc_scores:
                    print(f"   반환된 문서 수: {len(doc_scores)}개")
                    scores_str = ", ".join([f"{s:.4f}" for s in doc_scores])
                    print(f"   Similarity Scores: [{scores_str}]")
                else:
                    print(f"   (점수 정보 없음)")
                
                # 2. 관련성 판정 결과
                grade_results = result.get('grade_results', [])
                print(f"\n[2] 각 문서의 관련성 판정 결과:")
                if grade_results:
                    print(f"   판정 결과: {grade_results}")
                    yes_count = sum(1 for g in grade_results if g == 'YES')
                    no_count = sum(1 for g in grade_results if g == 'NO')
                    print(f"   관련있음(YES): {yes_count}개, 관련없음(NO): {no_count}개")
                
                # 3. 관련 문서 수
                filtered_docs = result.get('filtered_documents', [])
                relevant_docs_count = len(filtered_docs)
                print(f"\n[3] 관련 문서 수 (relevant_docs_count):")
                print(f"   {relevant_docs_count}개")
                
                # 4. 선택된 경로
                web_search_needed = result.get('web_search_needed', 'No')
                web_search_reason = result.get('web_search_reason', '')
                path = "WEB-SEARCH" if web_search_needed == 'Yes' else "INTERNAL"
                print(f"\n[4] 선택된 경로:")
                print(f"   → {path} 루트")
                if web_search_reason:
                    print(f"   이유: {web_search_reason}")
                else:
                    print(f"   이유: 관련 내부 문서 {relevant_docs_count}개 사용")
                
                # 5. 최종 답변 미리보기
                answer = result.get('answer', '(답변 없음)')
                answer_preview = answer[:80].replace('\n', ' ')
                print(f"\n[5] 최종 답변 (미리보기):")
                print(f"   {answer_preview}...")
                print()
            
            return {
                'answer': result.get('answer', '답변을 생성할 수 없습니다.'),
                'sources': result.get('sources', []),
                'num_sources': len(result.get('sources', [])),
                'document_scores': result.get('document_scores', []),
                'relevance_scores': result.get('relevance_scores', []),
                'grade_results': result.get('grade_results', []),
                'web_search_needed': result.get('web_search_needed', 'No'),
                'web_search_reason': result.get('web_search_reason', '')
            }
        except Exception as e:
            error_msg = f"오류가 발생했습니다: {str(e)}"
            if self.debug:
                print(f"\n❌ {error_msg}")
            return {
                'answer': error_msg,
                'sources': [],
                'num_sources': 0
            }


# 하위 호환성을 위한 기존 RAGPipeline 클래스 정의
class RAGPipeline:
    """
    RAG 파이프라인 클래스
    """
    def __init__(
        self,
        retriever: BaseRetriever,
        llm_model: str = "gpt-4o-mini",
        temperature: float = 0.0
    ):
        """
        Args:
            retriever: 문서 검색기
            llm_model: LLM 모델 이름
            temperature: LLM temperature
        """
        self.retriever = retriever
        self.llm = ChatOpenAI(model=llm_model, temperature=temperature)
        self.chain = self._build_chain()
    
    def _build_chain(self):
        """
        RAG 체인 구성
        """
        # Hallucination 방지를 위한 프롬프트
        prompt = ChatPromptTemplate.from_messages([
            ('system', '''당신은 제공된 문서를 기반으로 질문에 답변하는 AI 어시스턴트입니다.

중요한 규칙:
1. 반드시 제공된 문서(문맥)에 있는 정보만을 사용하여 답변하세요.
2. 문서에 없는 정보나 사실은 추측하지 마세요.
3. 문서에 정보가 충분하지 않거나 질문에 대한 답을 찾을 수 없으면, 솔직하게 "제공된 문서에는 이 정보가 없습니다" 또는 "문서를 확인할 수 없습니다"라고 답변하세요.
4. 답변은 한국어로 작성하세요.
5. 답변은 명확하고 간결하게 작성하세요.
6. 가능하면 문서의 내용을 인용하여 답변하세요.'''),
            ('human', '''문맥(참고 문서):
{context}

질문: {question}

위 문맥을 바탕으로 질문에 답변하세요. 문맥에 없는 내용은 답변하지 마세요.''')
        ])
        
        # 문서 포맷팅 함수
        def format_docs(docs: List[Document]) -> str:
            """검색된 문서들을 문자열로 포맷팅"""
            formatted = []
            for i, doc in enumerate(docs, 1):
                source = doc.metadata.get('file_name', 'unknown')
                department = doc.metadata.get('department', 'unknown')
                formatted.append(
                    f"[문서 {i} - 출처: {source}, 진료과: {department}]\n{doc.page_content}"
                )
            return "\n\n---\n\n".join(formatted)
        
        # RAG 체인 구성
        chain = (
            {
                "context": self.retriever | format_docs,
                "question": RunnablePassthrough()
            }
            | prompt
            | self.llm
            | StrOutputParser()
        )
        
        return chain
    
# 하위 호환성을 위한 기존 RAGPipeline 클래스 정의
class RAGPipeline:
    """
    기존 RAG 파이프라인 클래스 (하위 호환성)
    LangGraphRAGPipeline의 별칭으로 작동
    """
    def __init__(
        self,
        retriever: BaseRetriever,
        llm_model: str = "gpt-4o-mini",
        temperature: float = 0.0
    ):
        self._pipeline = LangGraphRAGPipeline(retriever, llm_model, temperature, debug=True)
    
    def rag_pipeline(self, query: str) -> str:
        return self._pipeline.rag_pipeline(query)
    
    def rag_pipeline_with_sources(self, query: str) -> Dict[str, Any]:
        return self._pipeline.rag_pipeline_with_sources(query)


def create_rag_pipeline(
    retriever: BaseRetriever,
    llm_model: str = "gpt-4o-mini",
    temperature: float = 0.0,
    use_langgraph: bool = True,
    debug: bool = True
) -> RAGPipeline:
    """
    RAG 파이프라인 생성
    
    Args:
        retriever: 문서 검색기
        llm_model: LLM 모델 이름
        temperature: LLM temperature
        use_langgraph: LangGraph CRAG 패턴 사용 여부 (기본값: True)
        debug: 디버깅 로그 출력 여부 (기본값: True)
        
    Returns:
        RAGPipeline 객체
    """
    return RAGPipeline(retriever, llm_model, temperature)


if __name__ == "__main__":
    # 테스트
    from embeddings import load_vectorstore, get_embedding_model
    from retrieval import create_retriever
    from dotenv import load_dotenv
    
    load_dotenv()
    
    # 벡터스토어 및 retriever 로드
    embedding_model = get_embedding_model("openai")
    vectorstore = load_vectorstore(
        embedding_model,
        persist_directory="./chroma_db",
        collection_name="rag_collection"
    )
    
    retriever = create_retriever(
        vectorstore,
        k=10,
        rerank_k=5,
        use_reranking=True,
        embedding_model=embedding_model
    )
    
    # LangGraph CRAG 파이프라인 생성
    print("LangGraph CRAG 파이프라인 초기화 중...\n")
    pipeline_crag = LangGraphRAGPipeline(retriever, debug=True)
    
    # 테스트 쿼리
    test_queries = [
        "강아지 몸에 두드러기가 났어요. 어떻게 하면 좋을까요?",
        "벼룩 알러지성 피부염의 증상은 무엇인가요?",
        "GPT-5의 최신 기능은?",  # 문서에 없는 쿼리 → 웹 검색 트리거
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n\n{'#'*80}")
        print(f"# 테스트 {i}/{len(test_queries)}")
        print(f"{'#'*80}")
        
        result = pipeline_crag.rag_pipeline_with_sources(query)
        
        print(f"\n📋 최종 답변:")
        print(f"\n{result['answer']}\n")

