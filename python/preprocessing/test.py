# Training 폴더 안의 라벨링 데이터 안의 폴더 안의 json 파일들 utf-8로 인코딩해서 불러오기
import os
import json
import chardet
import glob
import pandas as pd
from tqdm import tqdm

def read_json_with_encoding_detection(file_path):
    with open(file_path, 'rb') as f:
        raw_data = f.read()
        result = chardet.detect(raw_data)
        encoding = result['encoding']
    with open(file_path, 'r', encoding=encoding) as f:
        data = json.load(f)
    return data

def load_all_json_from_directory(base_directory_path):
    all_data = []
    
    # 하위 폴더들을 순회
    for sub_folder in os.listdir(base_directory_path):
        sub_folder_path = os.path.join(base_directory_path, sub_folder)
        
        # 디렉토리인 경우에만 처리
        if os.path.isdir(sub_folder_path):
            print(f"\nProcessing folder: {sub_folder}")
            json_files = glob.glob(os.path.join(sub_folder_path, '*.json'))
            
            for json_file in tqdm(json_files, desc=f"Loading from {sub_folder}"):
                try:
                    data = read_json_with_encoding_detection(json_file)
                    all_data.append(data)
                except Exception as e:
                    print(f"Error reading {json_file}: {e}")
    
    return all_data

# 예시 사용법
directory_path = 'C:\\LDG_CODES\\SKN20\\3rd_prj\\data\\59.반려견 성장 및 질병 관련 말뭉치 데이터\\3.개방데이터\\1.데이터\\Training\\02.라벨링데이터'
all_json_data = load_all_json_from_directory(directory_path)

# DataFrame으로 변환 (필요시)
df = pd.DataFrame(all_json_data)
print("\n=== Result ===")
print(df.head())
print(f"\nTotal rows: {df.shape[0]}, Total columns: {df.shape[1]}")

# CSV 파일로 저장
output_csv_path = '라벨링데이터_통합.csv'
df.to_csv(output_csv_path, index=False, encoding='utf-8-sig')
print(f"\n데이터가 '{output_csv_path}' 파일로 저장되었습니다.")