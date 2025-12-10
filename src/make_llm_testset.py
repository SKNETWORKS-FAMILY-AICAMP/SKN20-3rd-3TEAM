# -*- coding: utf-8 -*-
"""
RAGAS 평가용 질문-정답 테스트 데이터셋 생성 스크립트
- 벡터스토어에서 context 추출
- 추출된 context 기반으로 질문-정답 쌍 10개 생성
- 테스트 데이터셋 저장
"""

import os
import json
import random
import pandas as pd
from dotenv import load_dotenv
load_dotenv()

# 1. LLM 및 임베딩 모델 준비
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field

llm = ChatOpenAI(model="gpt-4.1")
embedding_model = OpenAIEmbeddings(model="text-embedding-3-large")

# 2. 벡터스토어 설정 - ChromaDB 벡터스토어 선택
# 옵션: "bge_m3" 또는 "openai"
VECTORSTORE_TYPE = "openai"  # "bge_m3" 또는 "openai" 선택

# 프로젝트 루트 경로 (스크립트 위치 기준)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

if VECTORSTORE_TYPE == "bge_m3":
    VECTOR_STORE_DIRS = [os.path.join(PROJECT_ROOT, "data", "ChromaDB_bge_m3")]
else:  # openai
    VECTOR_STORE_DIRS = [os.path.join(PROJECT_ROOT, "data", "ChromaDB_openai")]

# 3. 벡터스토어에서 context 추출
print("="*60)
print(f"벡터스토어({VECTORSTORE_TYPE.upper()})에서 context 추출 중...")
print("="*60)

all_contexts = []
MIN_CONTEXT_LEN = 200

for store_dir in VECTOR_STORE_DIRS:
    try:
        # 벡터스토어 디렉토리 존재 여부 확인
        if not os.path.exists(store_dir):
            print(f"✗ {store_dir}: 벡터스토어 디렉토리가 존재하지 않습니다")
            print(f"  → 먼저 vectorstore_{VECTORSTORE_TYPE}.py를 실행해 벡터스토어를 생성해주세요")
            continue
        
        # embedding_model 선택 (벡터스토어 타입에 맞춰)
        if VECTORSTORE_TYPE == "bge_m3":
            from langchain_community.embeddings import HuggingFaceEmbeddings
            current_embedding = HuggingFaceEmbeddings(model_name="BAAI/bge-m3")
            collection_name = "pet_health_qa_system_bge_m3"
        else:
            current_embedding = embedding_model
            collection_name = "pet_health_qa_system"
        
        # 사용 가능한 컬렉션 확인
        print(f"\n디버깅 정보:")
        print(f"  벡터스토어 경로: {store_dir}")
        print(f"  목표 컬렉션명: {collection_name}")
        
        vector_store = Chroma(
            embedding_function=current_embedding,
            persist_directory=store_dir,
            collection_name=collection_name
        )
        
        # 컬렉션에서 문서 개수 확인
        collection_count = vector_store._collection.count()
        print(f"  로드된 문서 개수: {collection_count}")
        
        if collection_count == 0:
            print(f"✗ {store_dir}: 벡터스토어가 비어있습니다 (저장된 문서 0개)")
            print(f"  → vectorstore_{VECTORSTORE_TYPE}.py를 실행하여 문서를 추가해주세요")
            continue
        
        docs = vector_store._collection.get(include=['documents'])['documents']
        contexts = [doc for doc in docs if len(doc) > MIN_CONTEXT_LEN]
        random.shuffle(contexts)
        # 10개 추출
        all_contexts.extend(contexts[:10])
        print(f"✓ {store_dir}: {min(10, len(contexts))}개 context 추출 (총 {collection_count}개 문서)")
    except Exception as e:
        print(f"✗ {store_dir} 추출 실패: {str(e)}")
        import traceback
        traceback.print_exc()

print(f"\n총 추출된 context 개수: {len(all_contexts)}\n")

# 4. 질문-정답 쌍 스키마 정의
class PETTestCase(BaseModel):
    user_input: str = Field(..., description="애완동물 관련 사용자 질문")
    reference: str = Field(..., description="질문에 대한 정확한 정답")

class PETTestDataset(BaseModel):
    test_cases: list[PETTestCase] = Field(..., description="질문-정답 쌍 리스트")

parser = JsonOutputParser(pydantic_object=PETTestDataset)

# 5. Context 기반 질문-정답 생성 프롬프트
template = """당신은 RAG 시스템 평가를 위한 고품질 테스트 데이터를 생성하는 AI 어시스턴트입니다.

다음 [Context]를 참고하여 1개의 질문-정답 쌍을 생성하세요.

생성 규칙:
1. 질문은 반드시 제공된 Context에 있는 정보를 바탕으로만 생성해야 합니다.
2. Context에 없는 내용을 질문이나 정답에 절대 포함하지 마세요.
3. 질문은 간결하고 명확하게 작성하세요.
4. 정답은 Context의 정보를 그대로 또는 요약하여 작성하세요.
5. Context를 수정하거나 변경하지 말고 그대로 참조하세요.

[Context]:
{context}

생성된 질문-정답 쌍을 다음 형식으로 반환하세요:
{format_instructions}
"""

prompt_template = PromptTemplate(
    template=template,
    partial_variables={"format_instructions": parser.get_format_instructions()}
)

eval_dataset_chain = prompt_template | llm | parser

# 6. Context당 1개씩 질문-정답 쌍 생성 (총 10개)
eval_dataset_list = []
failed_count = 0

print("="*60)
print("Context 기반 질문-정답 쌍 생성 중...")
print("="*60)

for idx, context in enumerate(all_contexts):
    try:
        print(f"\n[{idx + 1}/{len(all_contexts)}] Context에서 질문-정답 쌍 생성 중...", end=" ")
        
        result = eval_dataset_chain.invoke({
            "context": context
        })
        
        # 생성된 질문-정답 쌍 추출
        if hasattr(result, 'test_cases'):
            test_cases = result.test_cases
        else:
            test_cases = result.get('test_cases', [])
        
        if test_cases:
            eval_dataset_list.extend(test_cases)
            print(f"✓ 성공 (누적: {len(eval_dataset_list)}/{len(all_contexts)})")
        else:
            print(f"✗ 실패 (결과 없음)")
            failed_count += 1
        
    except Exception as e:
        print(f"✗ 실패: {str(e)[:80]}")
        failed_count += 1

print(f"\n생성된 질문-정답 쌍 개수: {len(eval_dataset_list)} (목표: {len(all_contexts)}, 실패: {failed_count})")

# 7. DataFrame으로 변환
data_for_df = []
for test_case in eval_dataset_list:
    # test_case가 dict인 경우와 Pydantic 객체인 경우 모두 처리
    if isinstance(test_case, dict):
        data_for_df.append({
            'user_input': test_case.get('user_input', ''),
            'reference': test_case.get('reference', '')
        })
    else:
        data_for_df.append({
            'user_input': test_case.user_input,
            'reference': test_case.reference
        })

eval_df = pd.DataFrame(data_for_df)

# 8. 테스트 데이터셋 저장
output_dir = os.path.join(PROJECT_ROOT, "output")
os.makedirs(output_dir, exist_ok=True)

# CSV 형식으로 저장
output_filename = os.path.join(output_dir, f"pet_test_dataset_{VECTORSTORE_TYPE}.csv")
eval_df.to_csv(output_filename, index=False, encoding='utf-8-sig')
print(f"\n✓ 테스트 데이터셋이 저장되었습니다: {output_filename}")

# 9. 데이터셋 통계 출력
print("\n" + "="*60)
print("생성된 테스트 데이터셋 정보")
print("="*60)
print(f"총 데이터셋 크기: {len(eval_df)}개")
print(f"데이터셋 컬럼: {eval_df.columns.tolist()}")
print(f"\n샘플 미리보기:")
print("-" * 60)
for idx, row in eval_df.iterrows():
    print(f"\n[샘플 {idx+1}]")
    print(f"질문: {row['user_input']}")
    reference_text = row['reference']
    if len(reference_text) > 100:
        print(f"정답: {reference_text[:100]}...")
    else:
        print(f"정답: {reference_text}")

# 11. JSON 형식으로도 저장
json_filename = os.path.join(output_dir, f"pet_test_dataset_{VECTORSTORE_TYPE}.json")
with open(json_filename, 'w', encoding='utf-8') as f:
    json.dump(data_for_df, f, ensure_ascii=False, indent=2)
print(f"✓ JSON 형식으로도 저장되었습니다: {json_filename}")

print("\n" + "="*60)
print("✅ 작업 완료!")
print("="*60)
