#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
from pathlib import Path

output = open('test_output.txt', 'w', encoding='utf-8')

try:
    output.write("시작\n")
    output.flush()
    
    output.write("sys.path 추가\n")
    sys.path.append(str(Path(__file__).parent))
    output.flush()
    
    output.write("import 시도\n")
    from src.hospital_handler import HospitalHandler
    output.write("import 성공\n")
    output.flush()
    
    output.write("HospitalHandler 생성 시도\n")
    output.flush()
    handler = HospitalHandler('data/raw/hospital/서울시_동물병원_인허가_정보.json')
    output.write(f"HospitalHandler 생성 성공, 병원 수: {len(handler.hospitals)}\n")
    output.flush()
    
except Exception as e:
    output.write(f"오류: {str(e)}\n")
    import traceback
    output.write(traceback.format_exc())
    output.flush()

finally:
    output.close()

