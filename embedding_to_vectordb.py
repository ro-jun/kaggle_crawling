import os
import json
import ollama
from pinecone import Pinecone
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
pc_api = os.getenv("PINECONE_API")
openai_api_key = os.getenv("OPENAI_API_KEY")

# Pinecone API 초기화
pc = Pinecone(api_key=pc_api)

# index 설정
index_name = "data-search-chatbot"

index = pc.Index(index_name)

# Ollama 임베딩 모델 초기화
# EMBEDDING_MODEL = "nomic-embed-text"
# 차원수가 768차원이라 유사도 계산이 정확하지가 않아서 openai로 변경
# EMBEDDING_MODEL = "text-embedding-3-small" # 1536
EMBEDDING_MODEL = "text-embedding-3-large" # 3072

client = OpenAI()

# JSON 폴더 경로
input_folder = "D:/kaggle/Kaggle_crawling/kaggle_datasets/comprehensive_description_datasets"

# 모든 JSON 파일 읽기
for filename in os.listdir(input_folder):
    if filename.endswith(".json"):
        filepath = os.path.join(input_folder, filename)

        # JSON 파일 로드
        with open(filepath, "r", encoding="utf-8") as f:
            datasets = json.load(f)

        # 각 데이터셋에 대해 임베딩 생성 및 Pinecone 저장
        for dataset in datasets:
            try:
                title = dataset.get("title", "Unknown Title")
                comprehensive_description = dataset.get("comprehensive_description", "")

                # # Ollama로 임베딩 생성
                # embedding_response = ollama.embeddings(
                #     model=EMBEDDING_MODEL,
                #     prompt=comprehensive_description
                # )
                # embedding = embedding_response["embedding"]

                # Openai
                embedding_response = client.embeddings.create(
                    input=comprehensive_description,
                    model=EMBEDDING_MODEL
                )

                embedding = embedding_response.data[0].embedding

                # Pinecone에 데이터 업로드
                index.upsert([
                    {
                        "id": title,  # 고유 ID로 title 사용
                        "values": embedding,  # 임베딩 벡터
                        "metadata": {
                            "title": title,
                            "file_type": dataset.get("file_type", ""),
                            "file_size": dataset.get("file_size", ""),
                            "url" : dataset.get("url", ""),
                            "comprehensive_description": comprehensive_description
                        }
                    }
                ])

                print(f"Data for '{title}' successfully upserted into Pinecone.")

            except Exception as e:
                print(f"Error processing dataset '{title}': {e}")
