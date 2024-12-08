import os
import pandas as pd
import json

# Kaggle 인증 파일 설정
os.environ["KAGGLE_CONFIG_DIR"] = os.path.expanduser("~/.kaggle")

# 데이터셋 정보 가져오기
def get_datasets_info(rows=300, file_type='csv'):
    # Kaggle API를 통해 데이터셋 목록 가져오기
    os.system(f"kaggle datasets list --file-type {file_type} --rows {rows} --json > datasets.json")
    
    # JSON 파일 읽기
    with open("datasets.json", "r") as f:
        datasets = json.load(f)
    
    dataset_info = []
    for dataset in datasets:
        dataset_info.append({
            "title": dataset.get("title"),
            "description": dataset.get("description"),
            "slug": dataset.get("ref")
        })
    
    return dataset_info

# 데이터셋 목록 확인
datasets = get_datasets_info()
print(datasets)
