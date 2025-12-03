#!/usr/bin/env python
# -*- coding: utf-8 -*-

# 모든 출력을 한 곳에서 제어
import io
import sys

# 새로운 버퍼 생성
buffer = io.StringIO()

try:
    # 원본 stdout/stderr 저장
    original_stdout = sys.stdout
    original_stderr = sys.stderr
    
    # stdout/stderr를 버퍼로 리디렉트
    sys.stdout = buffer
    sys.stderr = buffer
    
    # 테스트 코드
    print("테스트 시작")
    
    from src.hospital_handler import HospitalHandler
    print("import 성공")
    
    h = HospitalHandler()
    print(f"병원 수: {len(h.hospitals)}")
    
    stats = h.get_statistics()
    print(f"총 병원: {stats['total_hospitals']}")
    
    # 결과를 원래 stdout으로 복원
    sys.stdout = original_stdout
    sys.stderr = original_stderr
    
    # 버퍼 내용을 출력
    result = buffer.getvalue()
    print(result)
    
    # 파일에도 저장
    with open('final_test_output.txt', 'w', encoding='utf-8') as f:
        f.write(result)
    
except Exception as e:
    sys.stdout = original_stdout
    sys.stderr = original_stderr
    print(f"오류: {e}")
    import traceback
    traceback.print_exc()
    
    with open('final_test_output.txt', 'w', encoding='utf-8') as f:
        f.write(f"오류: {e}\n")
        f.write(traceback.format_exc())

