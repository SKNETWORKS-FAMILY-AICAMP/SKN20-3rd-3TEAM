"""
⚡ 빠른 일관성 체크 버전
간단하고 직관적으로 모델을 비교
"""

import pandas as pd
import numpy as np

def quick_analysis(csv_path='../output/ragas_evaluation_results_bge_m3.csv'):
    """빠른 분석"""
    
    # 📥 데이터 로드
    df = pd.read_csv(csv_path)
    
    print("\n" + "="*80)
    print("⚡ 일관성 빠른 체크 (Quick Analysis)")
    print("="*80 + "\n")
    
    # 📊 모델별로 분석
    for model in df['retriever_name'].unique():
        model_df = df[df['retriever_name'] == model]
        
        print(f"\n{'='*80}")
        print(f"🔍 {model}")
        print(f"{'='*80}")
        
        # 4개 지표
        indicators = ['context_recall', 'context_precision', 'faithfulness', 'answer_relevancy']
        
        total_score = 0
        
        for indicator in indicators:
            values = model_df[indicator].dropna()
            
            std = values.std()
            mean = values.mean()
            min_val = values.min()
            max_val = values.max()
            
            # ⭐ 일관성 점수 (간단한 버전)
            # 표준편차가 낮을수록, 최소값이 높을수록 좋음
            consistency_score = (1 - std) * 50 + (min_val) * 50
            consistency_score = max(0, min(100, consistency_score))
            
            total_score += consistency_score
            
            # 상태 이모지
            if consistency_score >= 80:
                status = "✅ 매우 좋음"
            elif consistency_score >= 70:
                status = "🟢 좋음"
            elif consistency_score >= 60:
                status = "🟡 보통"
            elif consistency_score >= 50:
                status = "🟠 낮음"
            else:
                status = "🔴 매우 낮음"
            
            print(f"\n   {indicator}:")
            print(f"      평균: {mean:.4f} | 표준편차: {std:.4f}")
            print(f"      범위: {min_val:.4f} ~ {max_val:.4f}")
            print(f"      일관성: {consistency_score:.1f}/100 {status}")
            
            # 극단값 경고
            if min_val == 0.0:
                print(f"      ⚠️  경고: 최소값이 0.0 (답변 실패!)")
            elif min_val < 0.5:
                print(f"      ⚠️  주의: 최소값이 {min_val:.2f}로 너무 낮음")
        
        # 모델 전체 점수
        total_score = total_score / len(indicators)
        
        if total_score >= 80:
            final_status = "⭐⭐⭐⭐⭐"
        elif total_score >= 70:
            final_status = "⭐⭐⭐⭐"
        elif total_score >= 60:
            final_status = "⭐⭐⭐"
        else:
            final_status = "⭐⭐"
        
        print(f"\n   {'─'*76}")
        print(f"   📈 전체 일관성 점수: {total_score:.1f}/100 {final_status}")
        print(f"   {'─'*76}")
    
    print("\n" + "="*80)
    print("🏆 최종 추천")
    print("="*80)
    print("""

1️⃣  앙상블 검색 (Ensemble Search)
    → 모든 지표에서 가장 안정적
    → 극단값(0.0)이 없음
    → 신뢰할 수 있는 성능

2️⃣  유사도 검색 (Similarity Search)
    → answer_relevancy가 우수
    → Context Precision이 불안정
    
3️⃣  MMR 검색
    → Faithfulness에서 0.0값 있음
    → 신뢰성 낮음

4️⃣  BM25 검색
    → Answer Relevancy에서 0.0값 있음
    → 일부 질문에 대해 완전히 실패
    """)
    print("="*80 + "\n")

if __name__ == "__main__":
    quick_analysis('../output/ragas_evaluation_results_bge_m3.csv')

