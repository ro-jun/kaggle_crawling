import json
import openai
import os
from dotenv import load_dotenv
import glob
from tqdm import tqdm

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# JSON 파일 경로 설정
input_folder = "D:/kaggle/Kaggle_crawling/kaggle_datasets/description_extended_datasets"
output_folder = "D:/kaggle/Kaggle_crawling/kaggle_datasets/comprehensive_description_datasets"
os.makedirs(output_folder, exist_ok=True)  # 결과 저장 폴더 생성
output_file = os.path.join(output_folder, "combined_results.json")

# 폴더 내 모든 JSON 파일 읽기 (glob 사용)
json_files = glob.glob(os.path.join(input_folder, "*.json"))

# 결과 저장 리스트
metadata_results = []

# 각 JSON 파일 처리
for filepath in json_files:
    with open(filepath, "r", encoding="utf-8") as f:
        datasets = json.load(f)

    # 각 데이터셋에 대해 프롬프트 실행
    for dataset in tqdm(datasets, desc=f"Processing datasets in {os.path.basename(filepath)}", leave=False):
        title = dataset.get("title", "Unknown Title")
        file_type_raw = dataset.get("file_type", "Unknown File Type")
        data_description = dataset.get("data_description", "No description available.")
        url = dataset.get("url", "Unknown url")
        # 파일 형식과 크기 추출
        file_type_parts = file_type_raw.split("·")
        file_type = "Unknown File Type"
        file_size = "Unknown Size"

        for part in file_type_parts:
            if "File" in part:
                file_type = part.strip()  # 예: "1 File (CSV)"
            elif "kB" in part or "MB" in part or "GB" in part:
                file_size = part.strip()  # 예: "10 kB"

        prompt = (
        f"Dataset Information:\n"
        f"Title: {title}\n"
        f"File Type: {file_type}\n"
        f"File Size: {file_size}\n"
        f"Description: {data_description}\n\n"
        f"Instructions:\n"
        f"1. You are an AI assistant tasked with generating comprehensive metadata descriptions for datasets."
        f"2. Write a detailed metadata description\n"
        f"3. Focus on the main purpose and key features of the dataset.\n"
        f"4. If necessary, expand on how the dataset can be applied in various use cases.\n"
        f"5. allow flexibility based on the dataset's complexity.\n"
        f"6. Do not restrict the description to three sentences; allow flexibility based on the dataset's complexity.\n"
        f"7. Please write the descriptions in Korean."
    )   

        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system",
                "content": f"{prompt}"},
            ]
        )

        # 결과 저장 (Pinecone DB에 적합한 구조)
        metadata_results.append({
            "title": title,
            "file_type": file_type,
            "file_size": file_size,
            "url" : url,
            "data_description": data_description,
            "comprehensive_description": response.choices[0].message.content
        })    

        print(f"Metadata for '{title}': {metadata_results[-1]}")

# 결과 저장 (Pinecone DB에 적합한 파일 형태)
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(metadata_results, f, ensure_ascii=False, indent=4)

print(f"Metadata results saved to {output_file}")