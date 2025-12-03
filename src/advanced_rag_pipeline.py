"""
고급 RAG 파이프라인 - 통합 시스템
질문 분류 → 유형별 처리 → 답변 생성
"""
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path

from src.question_classifier import QuestionClassifier, QuestionType
from src.medical_qa_handler import MedicalQAHandler
from src.hospital_handler import HospitalHandler
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage


class AdvancedRAGPipeline:
    """고급 RAG 통합 파이프라인"""
    
    def __init__(
        self,
        vectorstore: Any,
        hospital_json_path: str = "data/raw/hospital/서울시_동물병원_인허가_정보.json",
        llm_model: str = "gpt-4o-mini",
        score_threshold: float = 0.6
    ):
        """
        Args:
            vectorstore: Chroma 벡터스토어
            hospital_json_path: 병원 정보 JSON 경로
            llm_model: LLM 모델명
            score_threshold: 의료 질문의 근거 충분도 기준점
        """
        self.vectorstore = vectorstore
        self.llm = ChatOpenAI(model=llm_model, temperature=0.0)
        
        # 각 유형별 핸들러 초기화
        self.classifier = QuestionClassifier(llm_model=llm_model)
        self.medical_handler = MedicalQAHandler(
            vectorstore=vectorstore,
            llm_model=llm_model,
            score_threshold=score_threshold
        )
        self.hospital_handler = HospitalHandler(hospital_json_path=hospital_json_path)
        
        self.general_llm = ChatOpenAI(model=llm_model, temperature=0.0)
    
    def _handle_general_question(self, query: str) -> Dict[str, Any]:
        """
        일반 질문 처리 (타입 C)
        
        Args:
            query: 사용자 질문
            
        Returns:
            처리 결과
        """
        print(f"\n[일반 질문 처리] {query}")
        print("-" * 60)
        
        general_prompt = f"""당신은 반려동물 전문 QA 어시스턴트입니다.
다음 질문에 대해 정확하고 도움이 되는 답변을 제공하세요.

질문: {query}

주의:
- 의료 관련 질문이 아님을 확인했습니다.
- 정확하고 신뢰할 수 있는 정보 제공
- 필요시 전문가 상담 권유"""
        
        response = self.general_llm.invoke([HumanMessage(content=general_prompt)])
        
        return {
            'question': query,
            'question_type': 'C',
            'timestamp': datetime.now().isoformat(),
            'answer': response.content,
            'sources': [],
            'used_external_search': False
        }
    
    def _format_medical_answer(self, result: Dict[str, Any]) -> str:
        """
        의료 질문 답변 포맷팅
        
        Args:
            result: 의료 핸들러의 결과
            
        Returns:
            포맷된 답변
        """
        formatted = f"""
{result['answer']}

{'─' * 60}
📊 근거 정보:
  • 근거 점수: {result['relevance_score']:.1%}
  • 내부 문서: {result['internal_search_results']}개
  • 웹 검색 활용: {'예' if result['used_web_search'] else '아니오'}
  
📚 주요 출처:
"""
        for i, source in enumerate(result['sources'][:3], 1):
            if source.get('is_web_source'):
                formatted += f"  {i}. [웹] {source.get('title', 'Unknown')} ({source.get('source', 'Unknown')})\n"
            else:
                metadata = source.get('metadata', {})
                score = source.get('relevance_score', 0)
                formatted += f"  {i}. {metadata.get('file_name', 'Unknown')} ({score:.0%} 관련성)\n"
                if metadata.get('department'):
                    formatted += f"     부서: {metadata['department']}\n"
        
        return formatted
    
    def _format_hospital_answer(self, result: Dict[str, Any]) -> str:
        """
        병원 질문 답변 포맷팅
        
        Args:
            result: 병원 핸들러의 결과
            
        Returns:
            포맷된 답변
        """
        return result['response']
    
    def process_question(self, query: str) -> Dict[str, Any]:
        """
        질문 처리 메인 함수
        
        Args:
            query: 사용자 질문
            
        Returns:
            처리 결과
        """
        print("\n" + "=" * 80)
        print(f"🤖 질문 처리 시작")
        print("=" * 80)
        print(f"질문: {query}\n")
        
        # 1단계: 질문 분류
        print("1️⃣ 질문 유형 분류 중...")
        question_type, confidence, reason = self.classifier.classify(query)
        print(f"  분류 결과: {question_type.name} (신뢰도: {confidence:.2f})")
        print(f"  사유: {reason}\n")
        
        # 2단계: 유형별 처리
        if question_type == QuestionType.MEDICAL:
            print("2️⃣ 의료 질문 처리 모듈 실행...")
            result = self.medical_handler.handle_medical_question(query)
            result['classification_confidence'] = confidence
            result['formatted_answer'] = self._format_medical_answer(result)
        
        elif question_type == QuestionType.HOSPITAL:
            print("2️⃣ 병원/지도 질문 처리 모듈 실행...")
            result = self.hospital_handler.handle_hospital_question(query)
            result['classification_confidence'] = confidence
            result['formatted_answer'] = self._format_hospital_answer(result)
        
        else:  # QuestionType.GENERAL
            print("2️⃣ 일반 질문 처리 모듈 실행...")
            result = self._handle_general_question(query)
            result['classification_confidence'] = confidence
            result['formatted_answer'] = result['answer']
        
        # 3단계: 메타데이터 추가
        result['classification_type'] = question_type.name
        result['classification_reason'] = reason
        
        return result
    
    def interactive_mode(self):
        """
        대화형 모드
        """
        print("\n" + "=" * 80)
        print("🐾 반려동물 전문 QA 어시스턴트")
        print("=" * 80)
        print("\n질문을 입력하세요. (종료: quit, exit, 종료)\n")
        
        while True:
            try:
                user_input = input("\n💬 질문: ").strip()
                
                if user_input.lower() in ['quit', 'exit', '종료', 'q']:
                    print("\n감사합니다! 프로그램을 종료합니다. 🐾")
                    break
                
                if not user_input:
                    continue
                
                # 질문 처리
                result = self.process_question(user_input)
                
                # 결과 출력
                print("\n" + "=" * 80)
                print("📝 답변")
                print("=" * 80)
                print(result['formatted_answer'])
                print("\n" + "=" * 80)
                
            except KeyboardInterrupt:
                print("\n\n프로그램을 종료합니다. 🐾")
                break
            except Exception as e:
                print(f"\n❌ 오류 발생: {str(e)}")
                import traceback
                traceback.print_exc()
    
    def batch_process_questions(self, questions: List[str]) -> List[Dict[str, Any]]:
        """
        여러 질문을 배치 처리
        
        Args:
            questions: 질문 리스트
            
        Returns:
            결과 리스트
        """
        results = []
        
        for i, question in enumerate(questions, 1):
            print(f"\n[{i}/{len(questions)}] 처리 중...")
            result = self.process_question(question)
            results.append(result)
            
            # 결과 요약
            print(f"  ✓ 유형: {result['classification_type']}")
            print(f"  ✓ 신뢰도: {result['classification_confidence']:.2f}\n")
        
        return results
    
    def save_results(self, results: List[Dict[str, Any]], output_path: str = "results.json"):
        """
        처리 결과를 JSON으로 저장
        
        Args:
            results: 결과 리스트
            output_path: 저장 경로
        """
        # datetime 객체는 JSON 직렬화 불가능하므로 문자열로 변환
        def serialize_result(result):
            serialized = {}
            for key, value in result.items():
                if isinstance(value, datetime):
                    serialized[key] = value.isoformat()
                elif isinstance(value, dict):
                    serialized[key] = serialize_result(value)
                elif isinstance(value, list):
                    serialized[key] = [serialize_result(item) if isinstance(item, dict) else item 
                                      for item in value]
                else:
                    serialized[key] = value
            return serialized
        
        serialized_results = [serialize_result(r) for r in results]
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(serialized_results, f, ensure_ascii=False, indent=2)
        
        print(f"\n✓ 결과를 {output_path}에 저장했습니다.")

