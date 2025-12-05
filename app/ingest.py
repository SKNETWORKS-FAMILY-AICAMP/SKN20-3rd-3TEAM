"""
JSON 데이터 로딩 및 벡터스토어 생성 스크립트
"""
import json
from pathlib import Path
from typing import List, Dict, Any
from langchain.schema import Document
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from app.config import settings, JSON_DATA_DIR, VECTOR_STORE_DIR


def load_json_files(data_dir: Path) -> List[Dict[str, Any]]:
    """
    JSON 파일들을 로드하여 리스트로 반환

    Args:
        data_dir: JSON 파일들이 있는 디렉토리

    Returns:
        List[Dict]: 로드된 JSON 데이터 리스트
    """
    all_data = []
    json_files = list(data_dir.glob("*.json"))

    if not json_files:
        raise FileNotFoundError(f"'{data_dir}' 디렉토리에 JSON 파일이 없습니다.")

    print(f"총 {len(json_files)}개의 JSON 파일을 찾았습니다.")

    for json_file in json_files:
        try:
            with open(json_file, 'r', encoding='utf-8-sig') as f:
                data = json.load(f)

                # 리스트면 extend, 딕셔너리면 append
                if isinstance(data, list):
                    all_data.extend(data)
                else:
                    all_data.append(data)

            print(f"✓ {json_file.name} 로드 완료")

        except Exception as e:
            print(f"✗ {json_file.name} 로드 실패: {e}")

    print(f"\n총 {len(all_data)}개의 데이터를 로드했습니다.")
    return all_data


def convert_to_documents(data_list: List[Dict[str, Any]]) -> List[Document]:
    """
    JSON 데이터를 LangChain Document 객체로 변환

    Args:
        data_list: JSON 데이터 리스트

    Returns:
        List[Document]: 변환된 Document 리스트
    """
    documents = []

    for idx, item in enumerate(data_list):
        # JSON 구조에 맞게 텍스트 구성 (유연하게 처리)
        text_parts = []

        # 증상 정보
        if 'symptom' in item:
            text_parts.append(f"증상: {item['symptom']}")

        # 질병명
        if 'disease' in item:
            text_parts.append(f"질병명: {item['disease']}")

        # 설명
        if 'description' in item:
            text_parts.append(f"설명: {item['description']}")

        # 응급처치/대처법
        if 'first_aid' in item:
            text_parts.append(f"응급처치: {item['first_aid']}")

        # 병원 방문 시기
        if 'when_to_go_hospital' in item:
            text_parts.append(f"병원 방문 시기: {item['when_to_go_hospital']}")

        # 기타 필드들도 포함
        for key, value in item.items():
            if key not in ['symptom', 'disease', 'description', 'first_aid', 'when_to_go_hospital']:
                if isinstance(value, str):
                    text_parts.append(f"{key}: {value}")

        # 텍스트 결합
        page_content = "\n\n".join(text_parts)

        # 메타데이터 구성
        metadata = {
            "source": f"dog_symptom_data_{idx}",
            "disease": item.get('disease', 'Unknown'),
            "symptom": item.get('symptom', 'Unknown')
        }

        documents.append(Document(
            page_content=page_content,
            metadata=metadata
        ))

    print(f"{len(documents)}개의 Document로 변환했습니다.")
    return documents


def create_vector_store(documents: List[Document], persist_directory: Path) -> Chroma:
    """
    Document 리스트로부터 벡터스토어 생성 (배치 처리)
    
    Args:
        documents: Document 리스트
        persist_directory: 벡터스토어 저장 경로
        
    Returns:
        Chroma: 생성된 벡터스토어
    """
    # 텍스트 분할 (긴 문서 처리용)
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.CHUNK_SIZE,
        chunk_overlap=settings.CHUNK_OVERLAP,
        length_function=len,
    )
    
    split_docs = text_splitter.split_documents(documents)
    print(f"문서를 {len(split_docs)}개의 청크로 분할했습니다.")
    
    # OpenAI 임베딩 모델 초기화 (배치 크기 제한)
    embeddings = OpenAIEmbeddings(
        model=settings.OPENAI_EMBEDDING_MODEL,
        openai_api_key=settings.OPENAI_API_KEY,
        chunk_size=100  # 한 번에 100개씩만 처리
    )
    
    # Chroma 벡터스토어 생성 (배치 처리)
    print("벡터스토어를 생성하고 있습니다... (시간이 걸릴 수 있습니다)")
    
    # 배치 크기 설정 (한 번에 50개씩 처리)
    batch_size = 50
    total_batches = (len(split_docs) + batch_size - 1) // batch_size
    
    vectorstore = None
    
    for i in range(0, len(split_docs), batch_size):
        batch_docs = split_docs[i:i + batch_size]
        batch_num = (i // batch_size) + 1
        
        print(f"  배치 {batch_num}/{total_batches} 처리 중... ({len(batch_docs)}개 문서)")
        
        if vectorstore is None:
            # 첫 번째 배치: 새로 생성
            vectorstore = Chroma.from_documents(
                documents=batch_docs,
                embedding=embeddings,
                persist_directory=str(persist_directory),
                collection_name="dog_symptoms"
            )
        else:
            # 이후 배치: 기존 벡터스토어에 추가
            vectorstore.add_documents(batch_docs)
    
    print(f"벡터스토어가 '{persist_directory}'에 저장되었습니다.")
    return vectorstore


def main():
    """메인 실행 함수"""
    try:
        print("=" * 60)
        print("강아지 증상 데이터 벡터스토어 생성 시작")
        print("=" * 60)

        # 1. JSON 파일 로드
        print("\n[1단계] JSON 파일 로드 중...")
        data_list = load_json_files(JSON_DATA_DIR)

        # 2. Document 변환
        print("\n[2단계] Document 객체로 변환 중...")
        documents = convert_to_documents(data_list)

        # 3. 벡터스토어 생성
        print("\n[3단계] 벡터스토어 생성 중...")
        vectorstore = create_vector_store(documents, VECTOR_STORE_DIR)

        # 4. 테스트 검색
        print("\n[4단계] 테스트 검색 수행 중...")
        test_query = "기침을 하고 숨을 헐떡입니다"
        results = vectorstore.similarity_search(test_query, k=2)

        print(f"\n테스트 쿼리: '{test_query}'")
        print(f"검색 결과 {len(results)}개:")
        for i, doc in enumerate(results, 1):
            print(f"\n--- 결과 {i} ---")
            print(f"질병: {doc.metadata.get('disease', 'N/A')}")
            print(f"내용 미리보기: {doc.page_content[:200]}...")

        print("\n" + "=" * 60)
        print("벡터스토어 생성 완료!")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        raise


if __name__ == "__main__":
    main()
