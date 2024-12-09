import json
from langchain_ollama import ChatOllama
from langchain_core.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain_core.prompts import ChatPromptTemplate, HumanMessagePromptTemplate, SystemMessagePromptTemplate
import os

# JSON 파일 경로 설정
input_file = "D:/kaggle/Kaggle_crawling/kaggle_datasets/description_extended_datasets/test.json"
output_folder = "D:/kaggle/Kaggle_crawling/kaggle_datasets/comprehensive_description_datasets"
os.makedirs(output_folder, exist_ok=True)  # 폴더 생성
output_file = os.path.join(output_folder, "test.json")

# JSON 데이터 로드
with open(input_file, "r", encoding="utf-8") as f:
    datasets = json.load(f)

# 데이터에 대한 종합 설명(메타데이터) 생성 LLM
comprehensive_description_llm = ChatOllama(
    model="Qwen2.5-7B_q80:latest",
    callbacks=[StreamingStdOutCallbackHandler()]
)

# 프롬프트 템플릿 정의
prompt_template = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template("You are an AI assistant tasked with generating comprehensive metadata descriptions for datasets. Please write the descriptions in Korean."),
    HumanMessagePromptTemplate.from_template(
        "Dataset Information:\n"
        "Title: {title}\n"
        "File Type: {file_type}\n"
        "File Size: {file_size}\n"
        "Description: {data_description}\n\n"
        "Instructions:\n"
        "1. Create a detailed yet concise metadata description for this dataset.\n"
        "2. Ensure the description is no longer than three sentences.\n"
        "3. If necessary, provide suggestions for how the dataset could be used."
    )
])

# 결과 저장 리스트
metadata_results = []

# 각 데이터셋에 대해 프롬프트 실행
for dataset in datasets:
    try:
        title = dataset.get("title", "Unknown Title")
        file_type_raw = dataset.get("file_type", "Unknown File Type")
        data_description = dataset.get("data_description", "No description available.")  # 추출은 하되 저장하지 않음
        url = dataset.get("url", "Unknow url")
        # 파일 형식과 크기 추출
        file_type_parts = file_type_raw.split("·")
        file_type = "Unknown File Type"
        file_size = "Unknown Size"

        for part in file_type_parts:
            if "File" in part:
                file_type = part.strip()  # 예: "1 File (CSV)"
            elif "kB" in part or "MB" in part or "GB" in part:
                file_size = part.strip()  # 예: "10 kB"

        # 프롬프트 생성
        prompt = prompt_template.invoke({
            "title": title,
            "file_type": file_type,
            "file_size": file_size,
            "data_description": data_description,
            "url": url
        })

        # LLM 호출로 종합 설명 생성 (AIMessage 객체에서 텍스트 추출)
        comprehensive_description_data = comprehensive_description_llm.invoke(prompt).content

        # 결과 저장 (Pinecone DB에 적합한 구조)
        metadata_results.append({
            "title": title,
            "file_type": file_type,
            "file_size": file_size,
            "url" : url,
            "data_description": data_description,
            "comprehensive_description": comprehensive_description_data
        })

        print(f"Metadata for '{title}' generated successfully.")

    except Exception as e:
        print(f"Error generating metadata for '{title}': {e}")

# 결과 저장 (Pinecone DB에 적합한 파일 형태)
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(metadata_results, f, ensure_ascii=False, indent=4)

print(f"Metadata results saved to {output_file}")