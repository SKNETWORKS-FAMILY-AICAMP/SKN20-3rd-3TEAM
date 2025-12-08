"""
Evaluation Controller Module
응답 품질 평가 및 흐름 제어

역할:
  - 다차원 응답 품질 평가 (정확도, 명확성, 완전성, 안전성)
  - 평가 결과 기반 다음 액션 결정
  - 메트릭 수집 및 로깅
  - 응답 개선 피드백 생성
"""

from typing import Dict, Literal, Tuple
from datetime import datetime


def evaluate_response(response: str) -> Dict[str, any]:
    """응답을 4개 차원으로 평가"""
    print(f"⚖️  [evaluate_response] 응답 평가 중...\n")
    
    scores = {
        'accuracy': check_accuracy(response),
        'clarity': check_clarity(response),
        'completeness': check_completeness(response),
        'safety': check_safety_guidelines(response)['passed']
    }
    
    average_score = sum(scores.values()) / len(scores)
    passed = average_score >= 0.75
    feedback = generate_feedback(scores, response)
    
    evaluation = {
        'pass': passed,
        'scores': scores,
        'average_score': average_score,
        'feedback': feedback,
        'reason': '평가 완료'
    }
    
    print(f"✓ 평가 완료")
    print(f"  - 정확도: {scores['accuracy']:.0%}")
    print(f"  - 명확성: {scores['clarity']:.0%}")
    print(f"  - 완전성: {scores['completeness']:.0%}")
    print(f"  - 안전성: {scores['safety']:.0%}")
    print(f"  - 평균: {average_score:.0%}")
    print(f"  - 판정: {'✅ 통과' if passed else '🔄 재작성 필요'}\n")
    
    return evaluation


def check_accuracy(response: str) -> float:
    """응답의 정확도 평가"""
    if len(response) > 100:
        accuracy = 0.85
    else:
        accuracy = 0.65
    return accuracy


def check_clarity(response: str) -> float:
    """응답의 명확성 평가"""
    if len(response) > 50:
        clarity = 0.80
    else:
        clarity = 0.70
    return clarity


def check_completeness(response: str) -> float:
    """응답의 완전성 평가"""
    if len(response) > 200:
        completeness = 0.85
    else:
        completeness = 0.70
    return completeness


def check_safety_guidelines(response: str) -> Dict[str, any]:
    """응답이 안전 지침을 준수하는지 평가"""
    print(f"🛡️  [check_safety_guidelines] 안전성 검사\n")
    
    has_disclaimer = any(kw in response for kw in ['면책', '수의사 진료', '전문가 상담'])
    has_emergency_warning = any(kw in response for kw in ['응급', '즉시', '119', '병원 방문'])
    
    issues = []
    if not has_disclaimer:
        issues.append("의료 면책 조항 누락")
    if not has_emergency_warning and '증상' in response:
        issues.append("응급 경고 표시 부족")
    
    safety_score = 0.9 if has_disclaimer else 0.7
    
    safety_result = {
        'passed': safety_score,
        'has_disclaimer': has_disclaimer,
        'has_emergency_warning': has_emergency_warning,
        'issues': issues
    }
    
    print(f"  - 면책 조항: {'✓' if has_disclaimer else '✗'}")
    print(f"  - 응급 경고: {'✓' if has_emergency_warning else '✗'}")
    print(f"  - 안전도: {safety_score:.0%}")
    print(f"  - 문제: {len(issues)}개\n")
    
    return safety_result


def determine_next_action(
    response: str,
    evaluation: Dict[str, any]
) -> Literal["accept", "rewrite", "escalate"]:
    """평가 결과 기반 다음 액션 결정"""
    avg_score = evaluation.get('average_score', 0)
    
    if avg_score >= 0.75:
        action = "accept"
    elif avg_score >= 0.50:
        action = "rewrite"
    else:
        action = "escalate"
    
    print(f"🎯 [determine_next_action] 점수: {avg_score:.0%} → 액션: {action}")
    
    return action


def generate_feedback(scores: Dict[str, float], response: str) -> str:
    """평가 점수 기반 개선 피드백 생성"""
    feedback_list = []
    
    if scores.get('accuracy', 1.0) < 0.7:
        feedback_list.append("정확도 개선 필요")
    if scores.get('clarity', 1.0) < 0.7:
        feedback_list.append("표현이 너무 복잡합니다")
    if scores.get('completeness', 1.0) < 0.7:
        feedback_list.append("더 자세한 설명 필요")
    if scores.get('safety', 1.0) < 0.7:
        feedback_list.append("의료 면책 조항 추가 필요")
    
    if len(response) > 500:
        feedback_list.append("답변이 길어요")
    
    feedback = " | ".join(feedback_list) if feedback_list else "응답이 우수합니다"
    
    return feedback


def collect_evaluation_metrics(
    response: str,
    evaluation: Dict[str, any],
    generation_time: float,
    rewrite_count: int
) -> Dict[str, any]:
    """평가 메트릭 수집 및 통계 생성"""
    
    metrics = {
        'response_length': len(response),
        'generation_time': generation_time,
        'rewrite_count': rewrite_count,
        'evaluation_scores': evaluation.get('scores', {}),
        'average_score': evaluation.get('average_score', 0),
        'passed_evaluation': evaluation.get('pass', False),
        'timestamp': datetime.now().isoformat()
    }
    
    print(f"📊 [collect_evaluation_metrics] 메트릭 수집 완료")
    print(f"  - 응답 길이: {metrics['response_length']} 문자")
    print(f"  - 생성 시간: {metrics['generation_time']:.2f}초")
    print(f"  - 재작성: {metrics['rewrite_count']}회")
    print(f"  - 평가 점수: {metrics['average_score']:.0%}")
    
    return metrics


# ==================== 엔트리 포인트 ====================
if __name__ == "__main__":
    """테스트 실행 (스켈레톤 데모)"""
    
    print("\n" + "="*60)
    print("⚖️  Evaluation Controller Module - 테스트")
    print("="*60 + "\n")
    
    test_response = """강아지 피부염은 피부 표면의 염증입니다.
    
주요 증상:
- 가려움증
- 피부 발적

치료 방법:
- 약물 치료
- 피부 관리

⚠️  이는 일반 정보이며 전문 수의사 진료를 권장합니다."""
    
    print("### 테스트 1: 평가 ###\n")
    evaluation = evaluate_response(test_response)
    print(f"평가 결과: {'✅ 통과' if evaluation['pass'] else '🔄 재작성'}\n")
    
    print("\n### 테스트 2: 안전성 검사 ###\n")
    safety = check_safety_guidelines(test_response)
    print(f"안전성 점수: {safety['passed']:.0%}\n")
    
    print("\n### 테스트 3: 다음 액션 결정 ###\n")
    action = determine_next_action(test_response, evaluation)
    print(f"결정: {action}\n")
    
    print("\n### 테스트 4: 메트릭 수집 ###\n")
    metrics = collect_evaluation_metrics(test_response, evaluation, 2.5, 1)
    print()
    
    print("="*60)
    print("✅ 테스트 완료!")
    print("="*60)

