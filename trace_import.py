#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import traceback
import os

output = open('import_trace.txt', 'w', encoding='utf-8')

try:
    output.write("Python 버전: " + sys.version + "\n")
    output.write("작업 디렉토리: " + os.getcwd() + "\n")
    output.write("os 모듈 로드됨\n")
    output.write("작업 디렉토리: " + os.getcwd() + "\n")
    
    output.write("sys.path:\n")
    for p in sys.path:
        output.write(f"  {p}\n")
    
    output.write("\nimport json 시도\n")
    import json
    output.write("json 로드 성공\n")
    
    output.write("import datetime 시도\n")
    from datetime import datetime
    output.write("datetime 로드 성공\n")
    
    output.write("from typing import Dict 시도\n")
    from typing import Dict, List, Any, Optional
    output.write("typing 로드 성공\n")
    
    output.write("\nfrom src.hospital_handler import HospitalHandler 시도\n")
    output.flush()
    
    from src.hospital_handler import HospitalHandler
    output.write("HospitalHandler 로드 성공\n")
    output.flush()
    
except Exception as e:
    output.write(f"\n오류 발생:\n{str(e)}\n\n")
    output.write(traceback.format_exc())
    output.flush()

output.close()

