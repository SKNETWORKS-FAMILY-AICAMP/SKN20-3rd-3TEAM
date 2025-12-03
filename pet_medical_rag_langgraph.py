"""
🐾 반려동물 의료 RAG 어시스턴트 - LangGraph + CRAG 패턴
LangGraph 기반의 CRAG(Corrective RAG) 패턴 구현
웹 검색은 Tavily API 사용
"""

import os
import json
import warnings
warnings.filterwarnings("ignore")

from typing import List, Literal
from typing_extensions import TypedDict
from dotenv import load_dotenv
from pathlib import Path

# LangChain 관련 임포트
from langchain_core.documents import Document
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_community.retrievers import TavilySearchAPIRetriever

# LangGraph 관련 임포트
from langgraph.graph import StateGraph, START, END

# Pydantic
from pydantic import BaseModel, Field

# 환경설정
load_dotenv()

if not os.environ.get('OPENAI_API_KEY'):
    raise ValueError('❌ OPENAI_API_KEY 환경 변수 설정 필수')

if not os.environ.get('TAVILY_API_KEY'):
    raise ValueError('❌ TAVILY_API_KEY 환경 변수 설정 필수')

print("✅ API 키 확인 완료\n")

# ============================================================================
# 1️⃣ 상태 정의 (State)
# ============================================================================

class PetMedicalState(TypedDict):
    """반려동물 의료 RAG 상태"""
    question: str                          # 사용자 질문
    documents: List[Document]              # 벡터 저장소에서 검색된 문서
    filtered_documents: List[Document]     # 관련성 평가를 통과한 문서
    web_search_needed: str                 # 웹 검색 필요 여부 (Yes/No)
    context: str                           # 답변 생성용 컨텍스트
    answer: str                            # 최종 답변
    grade_results: List[str]               # 각 문서의 평가 결과
    classification: str                    # 질문 분류 (의료/병원/일반)
    sources: List[dict]                    # 답변에 사용된 출처

# ============================================================================
# 2️⃣ 문서 관련성 평가 모델
# ============================================================================

class GradeDocuments(BaseModel):
    """문서 관련성 평가 결과"""
    binary_score: str = Field(
        description="문서가 반려동물 의료 질문과 관련이 있으면 'yes', 없으면 'no'"
    )

# ============================================================================
# 3️⃣ 질병 데이터 로드 및 벡터 저장소 구축
# ============================================================================

print("📚 반려동물 질병 데이터 로드 중...")

# JSON 파일 경로
disease_dir = Path("data/raw/disease")

# 질병 데이터 로드
documents = []
if disease_dir.exists():
    for json_file in disease_dir.glob("*.json"):
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                disease_data = json.load(f)
                
                # 문서 내용 구성
                doc_content = f"""
질병명: {disease_data.get('name', 'N/A')}
설명: {disease_data.get('description', 'N/A')}

증상:
{', '.join(disease_data.get('symptoms', []))}

원인:
{', '.join(disease_data.get('causes', []))}

치료:
{', '.join(disease_data.get('treatment', []))}

예방:
{', '.join(disease_data.get('prevention', []))}

언제 병원을 방문해야 하나요:
{', '.join(disease_data.get('when_to_visit_vet', []))}

가정 관리:
{', '.join(disease_data.get('home_care', []))}
"""
                
                documents.append(
                    Document(
                        page_content=doc_content,
                        metadata={
                            "source": "internal_database",
                            "disease_name": disease_data.get('name', ''),
                            "file": json_file.name
                        }
                    )
                )
        except Exception as e:
            print(f"   ⚠️  파일 로드 실패 ({json_file.name}): {e}")

print(f"✅ {len(documents)}개 질병 문서 로드 완료\n")

# 텍스트 분할
print("🔪 문서 분할 중...")
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=100
)
doc_splits = text_splitter.split_documents(documents)
print(f"✅ {len(doc_splits)}개 청크로 분할 완료\n")

# 벡터 저장소 구축
print("🗂️  Chroma 벡터 저장소 구축 중...")
vectorstore = Chroma.from_documents(
    documents=doc_splits,
    collection_name='pet_medical_crag',
    embedding=OpenAIEmbeddings(model='text-embedding-3-small'),
    persist_directory="./chroma_pet_medical"
)
print(f"✅ 벡터 저장소 구축 완료\n")

# 리트리버 설정
retriever = vectorstore.as_retriever(search_kwargs={'k': 3})

# ============================================================================
# 4️⃣ LLM 및 Grader 설정
# ============================================================================

print("🤖 LLM 및 Grader 초기화 중...\n")

# 문서 관련성 평가 Grader
grader_llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
structured_grader = grader_llm.with_structured_output(GradeDocuments)

grade_prompt = ChatPromptTemplate.from_messages([
    ("system", """당신은 검색된 문서가 반려동물 의료 질문에 관련이 있는지 평가하는 전문가입니다.

평가 기준:
- 문서가 질문의 키워드나 의미와 연관되어 있으면 '관련있음'으로 평가
- 답변에 도움이 될 가능성이 조금이라도 있으면 '관련있음'
- 완전히 무관한 내용이면 '관련없음'

관대하게 평가하고, 약간의 연관성이라도 있으면 'yes'를 반환하세요."""),
    ("human", """질문: {question}
 
문서 내용:
{document}

이 문서가 질문과 관련이 있습니까? 'yes' 또는 'no'로만 답하세요""")
])

document_grader = grade_prompt | structured_grader

# 답변 생성 LLM
generation_llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)

# 질문 분류 LLM
classification_llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# ============================================================================
# 5️⃣ 노드 함수 정의
# ============================================================================

def classify_question_node(state: PetMedicalState) -> dict:
    """
    질문 분류 노드
    의료/병원/일반 질문 분류
    """
    print("\n   [CLASSIFY 노드] 질문 분류 중...")
    
    question = state['question']
    
    classify_prompt = ChatPromptTemplate.from_messages([
        ("system", """당신은 반려동물 관련 질문을 분류하는 전문가입니다.
        
질문을 다음 중 하나로 분류하세요:
- medical: 반려동물의 건강, 질병, 증상, 치료 등 의료 관련
- hospital: 동물병원 찾기, 위치, 진료시간 등 병원/지도 관련
- general: 반려동물 기본 관리, 훈련, 여행 등 일반 정보

분류만 반환하세요 (medical/hospital/general 중 하나)"""),
        ("human", f"질문: {question}\n\n분류:")
    ])
    
    chain = classify_prompt | classification_llm | StrOutputParser()
    classification = chain.invoke({}).lower().strip()
    
    # 분류 결과 검증
    if classification not in ['medical', 'hospital', 'general']:
        classification = 'general'
    
    print(f"   → 분류: {classification}")
    
    return {
        "classification": classification,
        "question": question
    }

def retrieve_node(state: PetMedicalState) -> dict:
    """
    문서 검색 노드
    벡터 저장소에서 관련 문서 검색
    """
    print("   [RETRIEVE 노드] 내부 문서 검색 중...")
    
    question = state['question']
    
    # 의료 질문이 아니면 검색 스킵
    if state.get('classification', 'general') != 'medical':
        print("   → 의료 질문 아님, 문서 검색 스킵")
        return {
            'documents': [],
            'question': question
        }
    
    documents = retriever.invoke(question)
    print(f"   → {len(documents)}개 문서 검색 완료")
    
    return {
        'documents': documents,
        'question': question
    }

def grade_documents_node(state: PetMedicalState) -> dict:
    """
    문서 관련성 평가 노드
    검색된 문서의 관련성을 LLM으로 평가
    """
    print("   [GRADE 노드] 문서 관련성 평가 중...")
    
    question = state['question']
    documents = state['documents']
    classification = state.get('classification', 'general')
    
    # 의료 질문 아니거나 문서 없으면 웹 검색
    if classification != 'medical' or len(documents) == 0:
        web_search_needed = "Yes"
        print(f"   → 웹 검색 필요! (의료: {classification == 'medical'}, 문서: {len(documents)}개)")
        return {
            "filtered_documents": [],
            "web_search_needed": web_search_needed,
            "grade_results": []
        }
    
    filtered_docs = []
    grade_results = []
    
    for i, doc in enumerate(documents, 1):
        try:
            score = document_grader.invoke({
                'question': question,
                'document': doc.page_content[:1000]  # 문서 일부만 평가
            })
            grade = score.binary_score.lower()
            
            if 'yes' in grade:
                filtered_docs.append(doc)
                grade_results.append("relevant")
                print(f"   → [{i}] ✅ 관련있음")
            else:
                grade_results.append("not_relevant")
                print(f"   → [{i}] ❌ 관련없음")
        except Exception as e:
            print(f"   → [{i}] ⚠️  평가 오류: {e}")
            grade_results.append("error")
    
    # 관련 문서가 없으면 웹 검색 필요
    if len(filtered_docs) == 0:
        web_search_needed = "Yes"
        print(f"   → 관련 문서 0개 → 웹 검색 필요!")
    else:
        web_search_needed = "No"
        print(f"   → {len(filtered_docs)}개 관련 문서 확보!")
    
    return {
        "filtered_documents": filtered_docs,
        "web_search_needed": web_search_needed,
        "grade_results": grade_results
    }

def web_search_node(state: PetMedicalState) -> dict:
    """
    웹 검색 노드
    Tavily API를 사용한 웹 검색
    """
    print("   [WEB_SEARCH 노드] Tavily로 웹 검색 중...")
    
    try:
        question = state["question"]
        
        # Tavily 검색 수행
        web_search = TavilySearchAPIRetriever(k=3)
        web_results = web_search.invoke(question)
        
        print(f"   → {len(web_results)}개 웹 검색 결과 획득")
        
        # 기존 필터링된 문서에 웹 검색 결과 추가
        filtered_docs = state.get("filtered_documents", [])
        for doc in web_results:
            doc.metadata["source"] = "web_search"
            doc.metadata["type"] = "external"
            filtered_docs.append(doc)
        
        print(f"   → 총 {len(filtered_docs)}개 문서로 통합")
        
        return {
            "filtered_documents": filtered_docs
        }
    
    except Exception as e:
        print(f"   ⚠️  웹 검색 오류: {e}")
        print("   → 기존 문서로 답변 생성 진행")
        return {
            "filtered_documents": state.get("filtered_documents", [])
        }

def generate_node(state: PetMedicalState) -> dict:
    """
    답변 생성 노드
    필터링된 문서를 바탕으로 최종 답변 생성
    """
    print("   [GENERATE 노드] 답변 생성 중...")
    
    question = state["question"]
    filtered_documents = state['filtered_documents']
    classification = state.get('classification', 'general')
    
    # 컨텍스트 구성
    if len(filtered_documents) > 0:
        context_parts = []
        for i, doc in enumerate(filtered_documents, 1):
            source = doc.metadata.get('source', 'unknown')
            disease_name = doc.metadata.get('disease_name', '')
            
            if disease_name:
                context_parts.append(f"[출처 {i}: {disease_name} ({source})]")
            else:
                context_parts.append(f"[출처 {i}: {source}]")
            
            context_parts.append(doc.page_content[:500])
        
        context = "\n\n---\n\n".join(context_parts)
    else:
        context = "관련 자료가 없습니다."
    
    # 질문 유형에 따른 프롬프트 설정
    if classification == 'medical':
        system_prompt = """당신은 반려동물 의료 전문가 어시스턴트입니다.

제공된 문맥을 바탕으로 반려동물 의료 질문에 답변하세요.

규칙:
1. 제공된 문맥 내의 정보를 우선적으로 사용하세요
2. 답변은 명확하고 구조화되게 작성하세요
3. 증상이나 치료법은 수의사 상담을 권장하세요
4. 긴급한 증상(심한 출혈, 호흡곤란 등)은 즉시 병원 방문을 권고하세요
5. 확실하지 않은 정보는 추측하지 마세요"""
    
    elif classification == 'hospital':
        system_prompt = """당신은 반려동물 병원 안내 전문가입니다.

병원 찾기 및 위치 정보에 대해 도움을 주세요.

규칙:
1. 제공된 정보를 바탕으로 병원을 추천하세요
2. 위치, 진료시간, 전화번호 등을 명확히 안내하세요
3. 24시간 응급 서비스 병원 정보가 있으면 강조하세요
4. 확실하지 않은 정보는 직접 전화로 확인하도록 권고하세요"""
    
    else:
        system_prompt = """당신은 친절한 반려동물 정보 어시스턴트입니다.

반려동물 관리, 훈련, 기본 정보에 대해 도움을 주세요.

규칙:
1. 명확하고 실용적인 조언을 제공하세요
2. 답변은 한국어로 구조화되게 작성하세요
3. 필요시 전문가 상담을 권장하세요
4. 확실하지 않은 정보는 추측하지 마세요"""
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", """문맥:
{context}

질문: {question}

답변:""")
    ])
    
    try:
        chain = prompt | generation_llm | StrOutputParser()
        answer = chain.invoke({
            "context": context,
            "question": question
        })
        print("   → 답변 생성 완료!")
    except Exception as e:
        print(f"   ⚠️  답변 생성 오류: {e}")
        answer = "죄송합니다. 답변 생성 중 오류가 발생했습니다."
    
    # 출처 정보 구성
    sources = []
    for doc in filtered_documents:
        source_info = {
            "name": doc.metadata.get('disease_name', 'Unknown'),
            "type": doc.metadata.get('source', 'unknown'),
            "file": doc.metadata.get('file', '')
        }
        sources.append(source_info)
    
    return {
        "context": context,
        "answer": answer,
        "sources": sources
    }

# ============================================================================
# 6️⃣ 조건부 엣지 함수
# ============================================================================

def decide_to_generate(state: PetMedicalState) -> Literal["generate", "web_search"]:
    """
    문서 평가 결과에 따라 다음 단계 결정
    - 관련 문서 있음 → generate
    - 관련 문서 없음 → web_search
    """
    print("\n   [DECISION] 다음 단계 결정 중...")
    
    web_search_needed = state.get("web_search_needed", "No")
    classification = state.get("classification", "general")
    
    # 의료 질문이 아니면 바로 답변 생성
    if classification != "medical":
        print("   → 의료 질문 아님, 바로 답변 생성")
        return "generate"
    
    if web_search_needed == "Yes":
        print("   → 웹 검색으로 이동")
        return "web_search"
    else:
        print("   → 답변 생성으로 이동")
        return "generate"

# ============================================================================
# 7️⃣ StateGraph 구성 및 컴파일
# ============================================================================

print("🔧 LangGraph 워크플로우 구성 중...\n")

# StateGraph 생성
workflow = StateGraph(PetMedicalState)

# 노드 추가
workflow.add_node("classify", classify_question_node)
workflow.add_node("retrieve", retrieve_node)
workflow.add_node("grade_documents", grade_documents_node)
workflow.add_node("web_search", web_search_node)
workflow.add_node("generate", generate_node)

# 엣지 추가
# START → classify → retrieve → grade_documents
workflow.add_edge(START, "classify")
workflow.add_edge("classify", "retrieve")
workflow.add_edge("retrieve", "grade_documents")

# 조건부 엣지: grade_documents 이후 분기
workflow.add_conditional_edges(
    "grade_documents",
    decide_to_generate,
    {
        "generate": "generate",
        "web_search": "web_search"
    }
)

# web_search → generate → END
workflow.add_edge("web_search", "generate")
workflow.add_edge("generate", END)

# 그래프 컴파일
app = workflow.compile()

print("✅ 워크플로우 컴파일 완료!\n")

# ============================================================================
# 8️⃣ 테스트 실행
# ============================================================================

def run_pet_medical_rag(question: str):
    """
    반려동물 의료 RAG 실행
    """
    print("\n" + "="*70)
    print(f"🐾 질문: {question}")
    print("="*70)
    
    # 초기 상태
    initial_state = {
        "question": question,
        "documents": [],
        "filtered_documents": [],
        "web_search_needed": "No",
        "context": "",
        "answer": "",
        "grade_results": [],
        "classification": "",
        "sources": []
    }
    
    # 워크플로우 실행
    print("\n🔄 CRAG 워크플로우 실행 중...\n")
    
    final_state = None
    for output in app.stream(initial_state):
        for node_name, node_output in output.items():
            # 각 노드 실행은 위의 print문으로 이미 표시됨
            pass
        final_state = output
    
    # 결과 출력
    print("\n" + "="*70)
    print("📋 최종 결과")
    print("="*70)
    
    if "generate" in final_state and final_state["generate"]:
        answer = final_state["generate"].get("answer", "답변 생성 실패")
        sources = final_state["generate"].get("sources", [])
    else:
        answer = "답변을 생성할 수 없습니다."
        sources = []
    
    print(f"\n💬 답변:\n{answer}")
    
    if sources:
        print(f"\n📚 참고 출처 ({len(sources)}개):")
        for i, source in enumerate(sources, 1):
            print(f"   {i}. {source.get('name', 'Unknown')} ({source.get('type', 'unknown')})")
    
    print("\n" + "="*70 + "\n")

# 테스트 질문
if __name__ == "__main__":
    test_questions = [
        "강아지가 계속 구토를 해요. 뭔가 잘못된 건가요?",
        "고양이 설사는 어떻게 치료해야 하나요?",
        "반려동물 알레르기 증상과 치료법을 알려주세요",
        "강남역 근처 24시간 동물병원을 찾아줘",
        "반려견과 함께 여행할 때 주의할 점은?"
    ]
    
    print("\n🐾 반려동물 의료 RAG 어시스턴트 테스트 시작\n")
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n{'='*70}")
        print(f"테스트 {i}/{len(test_questions)}")
        print(f"{'='*70}")
        
        try:
            run_pet_medical_rag(question)
        except Exception as e:
            print(f"\n❌ 테스트 실행 오류: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n✅ 모든 테스트 완료!")

