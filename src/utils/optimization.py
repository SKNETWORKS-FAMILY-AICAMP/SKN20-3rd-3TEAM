"""
RAG 시스템 성능 최적화 및 안정화 모듈
- 키워드 추출 (Query Re-writing)
- 불용어 제거 (Stopword Removal)
- 모델 및 전처리 결과 저장/로드
- 청크 사이즈 최적화
- 경로 관리
"""

import os
import pickle
import re
from typing import List, Optional, Dict, Any
from pathlib import Path

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

# KoNLPy 불용어 제거용 (설치 필요: pip install konlpy)
try:
    from konlpy.tag import Okt
    KONLPY_AVAILABLE = True
except ImportError:
    print("⚠️ KoNLPy가 설치되어 있지 않습니다. 불용어 제거 기능이 제한됩니다.")
    print("   설치 명령: pip install konlpy")
    KONLPY_AVAILABLE = False


# ============================================================================
# 5. 📂 경로 관리 (BASE_DIR 설정)
# ============================================================================

# 현재 파일의 절대 경로를 기준으로 BASE_DIR 설정
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

def get_project_path(*paths) -> str:
    """
    프로젝트 루트를 기준으로 상대 경로 생성
    
    Args:
        *paths: 경로 조각들
        
    Returns:
        절대 경로 문자열
        
    Example:
        get_project_path('data', 'chroma_db')
        -> 'C:/LDG_CODES/SKN20/SKN20-3rd-3TEAM/data/chroma_db'
    """
    return os.path.join(BASE_DIR, *paths)


# ============================================================================
# 4. 📐 청크 사이즈 최적화 설정
# ============================================================================

# 최적화된 청크 설정 (수의학 임상 문맥 유지)
CHUNK_SIZE = 512  # 토큰 기준
CHUNK_OVERLAP = 80  # 토큰 기준

# 한국어 문장 분리를 위한 구분자 우선순위
KOREAN_SEPARATORS = [
    "\n\n",  # 단락 구분
    "\n",    # 줄바꿈
    ". ",    # 문장 종료
    "? ",    # 의문문
    "! ",    # 감탄문
    "; ",    # 세미콜론
    ", ",    # 쉼표
    " ",     # 공백
    ""       # 마지막 수단
]


def create_optimized_text_splitter() -> RecursiveCharacterTextSplitter:
    """
    최적화된 텍스트 분할기 생성
    
    Returns:
        RecursiveCharacterTextSplitter 인스턴스
    """
    return RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        length_function=len,
        separators=KOREAN_SEPARATORS,
        is_separator_regex=False
    )


# ============================================================================
# 1. 🔑 키워드 추출 (Query Re-writing)
# ============================================================================

def extract_keywords_for_query(
    user_input: str,
    llm_model: Optional[ChatOpenAI] = None
) -> str:
    """
    사용자 질문에서 RAG 검색에 최적화된 핵심 키워드 추출
    
    Args:
        user_input: 사용자 원본 질문
        llm_model: 사용할 LLM 모델 (None이면 기본 모델 사용)
        
    Returns:
        띄어쓰기로 연결된 키워드 문자열
        
    Example:
        Input: "저희 강아지가 구토를 계속하고 황달 증상이 있어요"
        Output: "구토 황달 간질환 내과 성견"
    """
    if llm_model is None:
        llm_model = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.0,  # 일관된 키워드 추출
            max_tokens=150
        )
    
    # 키워드 추출 프롬프트
    keyword_prompt = f"""다음 반려동물 건강 질문에서 RAG 검색에 필요한 핵심 키워드만 추출하세요.

## 사용자 질문
{user_input}

## 추출 기준 (4가지 범주)
1. **질병명**: 의심되는 질환 (예: 위염, 간질환, 외이도염)
2. **증상**: 명확한 증상 키워드 (예: 구토, 설사, 황달, 기침)
3. **신체 부위**: 영향받는 부위 (예: 눈, 귀, 피부, 복부)
4. **연령대**: 자견/성견/노령견 (명시되지 않으면 생략)

## 출력 형식
**띄어쓰기로 구분된 키워드만** 출력하세요. 설명이나 문장 없이 키워드만 나열하세요.

예시:
- 입력: "3개월 된 강아지가 설사하고 토해요"
- 출력: "설사 구토 장염 자견 내과"

키워드:"""

    try:
        response = llm_model.invoke([HumanMessage(content=keyword_prompt)])
        keywords = response.content.strip()
        
        # 추가 정제: 불필요한 구두점 제거
        keywords = re.sub(r'[^\w\s]', '', keywords)
        keywords = re.sub(r'\s+', ' ', keywords)
        
        print(f"[키워드 추출] 원본: {user_input[:50]}...")
        print(f"[키워드 추출] 결과: {keywords}")
        
        return keywords
    
    except Exception as e:
        print(f"⚠️ 키워드 추출 실패: {e}")
        # 실패 시 원본 반환
        return user_input


# ============================================================================
# 2. 🗑️ 불용어 제거 (Stopword Removal)
# ============================================================================

# 한국어 의학 도메인 불용어 리스트
KOREAN_MEDICAL_STOPWORDS = {
    # 일반 불용어
    '이', '그', '저', '것', '수', '등', '및', '또는', '또', '때문',
    '위해', '통해', '대해', '관해', '따라', '의해', '로써', '부터',
    '까지', '마다', '조차', '만', '뿐', '에서', '에게', '한테',
    
    # 의학 문서 불용어
    '증례', '환자', '보호자', '수의사', '병원', '진료', '검사',
    '결과', '소견', '판단', '확인', '관찰', '필요', '가능',
    
    # 조사/어미
    '은', '는', '이', '가', '을', '를', '의', '에', '에서', '로', '으로',
    '와', '과', '도', '만', '부터', '까지', '하고', '하며', '되어',
}


def preprocess_text_with_stopwords(text: str) -> str:
    """
    텍스트에서 불용어 제거 (형태소 분석 기반)
    
    Args:
        text: 원본 텍스트
        
    Returns:
        불용어가 제거된 텍스트
        
    Example:
        Input: "강아지가 구토를 하고 있습니다"
        Output: "강아지 구토"
    """
    if not text or not text.strip():
        return ""
    
    # KoNLPy 사용 가능 여부 확인
    if not KONLPY_AVAILABLE:
        # KoNLPy 없을 경우 간단한 불용어 제거만 수행
        return _simple_stopword_removal(text)
    
    try:
        okt = Okt()
        
        # 형태소 분석
        morphs = okt.pos(text, norm=True, stem=True)
        
        # 명사, 동사, 형용사만 추출 (조사, 어미, 구두점 제거)
        filtered_words = []
        for word, pos in morphs:
            # 유의미한 품사만 선택
            if pos in ['Noun', 'Verb', 'Adjective']:
                # 불용어 제외
                if word not in KOREAN_MEDICAL_STOPWORDS and len(word) > 1:
                    filtered_words.append(word)
        
        # 띄어쓰기로 연결
        cleaned_text = ' '.join(filtered_words)
        
        return cleaned_text
    
    except Exception as e:
        print(f"⚠️ 형태소 분석 실패: {e}, 간단한 불용어 제거로 대체")
        return _simple_stopword_removal(text)


def _simple_stopword_removal(text: str) -> str:
    """
    간단한 불용어 제거 (KoNLPy 없을 때 대체 방법)
    
    Args:
        text: 원본 텍스트
        
    Returns:
        불용어가 제거된 텍스트
    """
    # 구두점 제거
    text = re.sub(r'[^\w\s]', ' ', text)
    
    # 단어 분리
    words = text.split()
    
    # 불용어 제거
    filtered_words = [
        word for word in words 
        if word not in KOREAN_MEDICAL_STOPWORDS and len(word) > 1
    ]
    
    return ' '.join(filtered_words)


# ============================================================================
# 3. 💾 모델 및 전처리 결과 저장/로드
# ============================================================================

def save_processed_documents(
    documents: List[Document],
    save_path: str
) -> None:
    """
    전처리된 Document 객체들을 pickle로 저장
    
    Args:
        documents: Document 객체 리스트
        save_path: 저장할 파일 경로
    """
    # 디렉토리가 없으면 생성
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    
    with open(save_path, 'wb') as f:
        pickle.dump(documents, f)
    
    print(f"✓ 전처리 결과 저장 완료: {save_path}")
    print(f"  - 문서 수: {len(documents)}개")


def load_processed_documents(load_path: str) -> Optional[List[Document]]:
    """
    저장된 Document 객체들을 pickle에서 로드
    
    Args:
        load_path: 로드할 파일 경로
        
    Returns:
        Document 객체 리스트 또는 None (파일 없을 시)
    """
    if not os.path.exists(load_path):
        print(f"ℹ️ 저장된 전처리 결과 없음: {load_path}")
        return None
    
    try:
        with open(load_path, 'rb') as f:
            documents = pickle.load(f)
        
        print(f"✓ 전처리 결과 로드 완료: {load_path}")
        print(f"  - 문서 수: {len(documents)}개")
        
        return documents
    
    except Exception as e:
        print(f"⚠️ 전처리 결과 로드 실패: {e}")
        return None


def manage_persistence(
    data_path: str,
    persist_dir: str,
    force_rebuild: bool = False
) -> Dict[str, Any]:
    """
    Vector DB 및 전처리 결과 영구 저장/로드 관리
    
    전체 흐름:
    1. Vector DB 존재 → 로드
    2. Vector DB 없음 + pkl 존재 → pkl 로드 → 임베딩 → Vector DB 저장
    3. 모두 없음 → 원천 데이터 로드 → 전처리 → pkl 저장 → 임베딩 → Vector DB 저장
    
    Args:
        data_path: 원천 데이터 경로
        persist_dir: Vector DB 저장 디렉토리
        force_rebuild: True면 캐시 무시하고 재구축
        
    Returns:
        {
            "documents": List[Document],
            "vectorstore": Chroma,
            "retriever": Retriever,
            "status": "loaded" | "created"
        }
    """
    from langchain_community.vectorstores import Chroma
    from langchain_openai import OpenAIEmbeddings
    
    pkl_path = get_project_path('data', 'processed_docs.pkl')
    
    # 강제 재구축 플래그
    if force_rebuild:
        print("🔄 강제 재구축 모드: 기존 캐시 무시")
        if os.path.exists(persist_dir):
            import shutil
            shutil.rmtree(persist_dir)
        if os.path.exists(pkl_path):
            os.remove(pkl_path)
    
    # ========================================================================
    # 1단계: Vector DB 존재 여부 확인
    # ========================================================================
    if os.path.exists(persist_dir) and os.path.exists(os.path.join(persist_dir, 'chroma.sqlite3')):
        print(f"✓ 기존 Vector DB 발견: {persist_dir}")
        print("  - Vector DB 로드 중...")
        
        try:
            embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
            vectorstore = Chroma(
                persist_directory=persist_dir,
                embedding_function=embeddings
            )
            retriever = vectorstore.as_retriever(
                search_type="similarity",
                search_kwargs={"k": 4}
            )
            
            print("✓ Vector DB 로드 완료")
            
            return {
                "documents": None,  # 이미 임베딩됨
                "vectorstore": vectorstore,
                "retriever": retriever,
                "status": "loaded"
            }
        
        except Exception as e:
            print(f"⚠️ Vector DB 로드 실패: {e}")
            print("  - 재구축 진행...")
    
    # ========================================================================
    # 2단계: pkl 파일 존재 여부 확인
    # ========================================================================
    documents = load_processed_documents(pkl_path)
    
    if documents is None:
        print(f"ℹ️ 전처리 결과 없음, 원천 데이터 로드 시작: {data_path}")
        
        # 원천 데이터 로드 및 전처리
        from data.preprocessing import load_multiple_departments
        
        documents = load_multiple_departments(
            base_path=data_path,
            departments=["내과", "외과", "안과", "치과", "피부과"],
            data_type="source",
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP
        )
        
        if not documents:
            raise ValueError(f"데이터 로드 실패: {data_path}")
        
        # 전처리 결과 저장
        save_processed_documents(documents, pkl_path)
    
    # ========================================================================
    # 3단계: Vector DB 구축
    # ========================================================================
    print(f"\n📊 Vector DB 구축 시작 (문서 수: {len(documents)}개)")
    
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    
    vectorstore = Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
        persist_directory=persist_dir
    )
    
    retriever = vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 4}
    )
    
    print(f"✓ Vector DB 구축 및 저장 완료: {persist_dir}")
    
    return {
        "documents": documents,
        "vectorstore": vectorstore,
        "retriever": retriever,
        "status": "created"
    }


# ============================================================================
# 통합 최적화 전처리 함수
# ============================================================================

def optimized_preprocess_text(text: str) -> str:
    """
    최적화된 전처리 파이프라인 (불용어 제거 + 정제)
    
    Args:
        text: 원본 텍스트
        
    Returns:
        전처리된 텍스트
    """
    if not text:
        return ""
    
    # 1. 특수문자 정제 (의학 용어 보존)
    text = re.sub(r'[\x00-\x08\x0b-\x0c\x0e-\x1f\x7f-\x9f]', '', text)
    
    # 2. 연속 공백 통합
    text = re.sub(r'\s+', ' ', text)
    
    # 3. 불용어 제거
    text = preprocess_text_with_stopwords(text)
    
    # 4. 최종 정제
    text = text.strip()
    
    return text


# ============================================================================
# 예제 사용법
# ============================================================================

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    
    print("="*80)
    print("RAG 시스템 최적화 모듈 테스트")
    print("="*80)
    
    # 1. 경로 관리 테스트
    print("\n[1] 경로 관리 테스트")
    print(f"BASE_DIR: {BASE_DIR}")
    print(f"Data Path: {get_project_path('data', 'chroma_db')}")
    
    # 2. 키워드 추출 테스트
    print("\n[2] 키워드 추출 테스트")
    test_query = "저희 강아지가 구토를 계속하고 황달 증상이 있어요. 3살 된 성견입니다."
    keywords = extract_keywords_for_query(test_query)
    print(f"추출된 키워드: {keywords}")
    
    # 3. 불용어 제거 테스트
    print("\n[3] 불용어 제거 테스트")
    test_text = "강아지가 구토를 하고 있습니다. 이것은 심각한 증상일 수 있습니다."
    cleaned = preprocess_text_with_stopwords(test_text)
    print(f"원본: {test_text}")
    print(f"정제: {cleaned}")
    
    # 4. 청크 분할 테스트
    print("\n[4] 청크 분할 테스트")
    splitter = create_optimized_text_splitter()
    print(f"청크 크기: {CHUNK_SIZE}, 오버랩: {CHUNK_OVERLAP}")
    
    # 5. 영구 저장 관리 테스트
    print("\n[5] 영구 저장 관리 테스트")
    print("manage_persistence() 함수는 실제 데이터가 있을 때 실행됩니다.")
    
    print("\n✓ 모든 테스트 완료")
