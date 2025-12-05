"""
RAG 오케스트레이터 - 메인 파이프라인
질문 분류 → 유형별 핸들러 라우팅 → 결과 포맷팅
"""
from typing import Dict, List, Any, Optional
from datetime import datetime
from .base import BasePipeline
from src.classifiers import QuestionClassifier, QuestionType
from src.handlers import MedicalHandler, HospitalHandler, GeneralHandler
from src.utils import get_logger, serialize_result

logger = get_logger(__name__)


class RAGOrchestrator(BasePipeline):
    """RAG 통합 오케스트레이터"""
    
    def __init__(
        self,
        vectorstore: Optional[Any] = None,
        hospital_json_path: Optional[str] = None,
        llm_model: str = "gpt-4o-mini",
        score_threshold: float = 0.6
    ):
        """
        Args:
            vectorstore: Chroma 벡터스토어 (의료 질문 처리용)
            hospital_json_path: 병원 JSON 경로
            llm_model: LLM 모델명
            score_threshold: 의료 질문 근거 충분도 기준점
        """
        logger.info("RAGOrchestrator 초기화 중...")
        
        # 질문 분류기 초기화
        self.classifier = QuestionClassifier(llm_model=llm_model)
        
        # 유형별 핸들러 초기화
        if vectorstore:
            self.medical_handler = MedicalHandler(
                vectorstore=vectorstore,
                llm_model=llm_model,
                score_threshold=score_threshold
            )
        else:
            logger.warning("벡터스토어가 없어 의료 핸들러 생성 스킵됨")
            self.medical_handler = None
        
        self.hospital_handler = HospitalHandler(hospital_json_path=hospital_json_path)
        self.general_handler = GeneralHandler(llm_model=llm_model)
        
        logger.info("RAGOrchestrator 초기화 완료")
    
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
    
    def process(self, query: str, **kwargs) -> Dict[str, Any]:
        """
        질문 처리 메인 함수
        
        Args:
            query: 사용자 질문
            **kwargs: 추가 파라미터 (예: latitude, longitude 등)
            
        Returns:
            처리 결과
        """
        logger.info(f"질문 처리 시작: {query[:50]}...")
        print("\n" + "=" * 80)
        print(f"🤖 질문 처리 시작")
        print("=" * 80)
        print(f"질문: {query}\n")
        
        # 1단계: 질문 분류
        logger.info("1단계: 질문 분류")
        print("1️⃣ 질문 유형 분류 중...")
        question_type, confidence, reason = self.classifier.classify(query)
        print(f"  분류 결과: {question_type.name} (신뢰도: {confidence:.2f})")
        print(f"  사유: {reason}\n")
        
        # 2단계: 유형별 처리
        if question_type == QuestionType.MEDICAL:
            logger.info("2단계: 의료 질문 처리")
            print("2️⃣ 의료 질문 처리 모듈 실행...")
            
            if not self.medical_handler:
                logger.error("의료 핸들러를 사용할 수 없습니다")
                result = {
                    'question': query,
                    'question_type': 'A',
                    'timestamp': datetime.now().isoformat(),
                    'answer': '의료 질문 처리를 위한 시스템이 준비되지 않았습니다.',
                    'sources': [],
                    'used_web_search': False,
                    'classification_confidence': confidence,
                    'classification_type': question_type.name,
                    'classification_reason': reason,
                    'formatted_answer': '의료 질문 처리를 위한 시스템이 준비되지 않았습니다.'
                }
            else:
                result = self.medical_handler.handle(query)
                result['classification_confidence'] = confidence
                result['formatted_answer'] = self._format_medical_answer(result)
        
        elif question_type == QuestionType.HOSPITAL:
            logger.info("2단계: 병원/지도 질문 처리")
            print("2️⃣ 병원/지도 질문 처리 모듈 실행...")
            result = self.hospital_handler.handle(query, **kwargs)
            result['classification_confidence'] = confidence
            result['formatted_answer'] = self._format_hospital_answer(result)
        
        else:  # QuestionType.GENERAL
            logger.info("2단계: 일반 질문 처리")
            print("2️⃣ 일반 질문 처리 모듈 실행...")
            result = self.general_handler.handle(query)
            result['classification_confidence'] = confidence
            result['formatted_answer'] = result['answer']
        
        # 3단계: 메타데이터 추가
        result['classification_type'] = question_type.name
        result['classification_reason'] = reason
        
        logger.info(f"질문 처리 완료: {question_type.name}")
        return result
    
    def batch_process(self, queries: List[str], **kwargs) -> List[Dict[str, Any]]:
        """
        여러 질문을 배치 처리
        
        Args:
            queries: 질문 리스트
            **kwargs: 추가 파라미터
            
        Returns:
            결과 리스트
        """
        logger.info(f"배치 처리 시작: {len(queries)}개 질문")
        results = []
        
        for i, question in enumerate(queries, 1):
            print(f"\n[{i}/{len(queries)}] 처리 중...")
            result = self.process(question, **kwargs)
            results.append(result)
            
            # 결과 요약
            print(f"  ✓ 유형: {result['classification_type']}")
            print(f"  ✓ 신뢰도: {result['classification_confidence']:.2f}\n")
        
        logger.info(f"배치 처리 완료: {len(results)}개 결과")
        return results
    
    def save_results(self, results: List[Dict[str, Any]], output_path: str = "results.json"):
        """
        처리 결과를 JSON으로 저장
        
        Args:
            results: 결과 리스트
            output_path: 저장 경로
        """
        import json
        
        logger.info(f"결과 저장 중: {output_path}")
        
        # 직렬화 가능한 형태로 변환
        serialized_results = [serialize_result(r) for r in results]
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(serialized_results, f, ensure_ascii=False, indent=2)
        
        logger.info(f"결과 저장 완료: {output_path}")
        print(f"\n✓ 결과를 {output_path}에 저장했습니다.")
    
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
                result = self.process(user_input)
                
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
                logger.error(f"오류 발생: {str(e)}")
                print(f"\n❌ 오류 발생: {str(e)}")
                import traceback
                traceback.print_exc()

