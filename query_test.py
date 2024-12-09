import os
from pinecone import Pinecone
from dotenv import load_dotenv
import ollama
from openai import OpenAI

# 환경 변수 로드
load_dotenv()
pc_api = os.getenv("PINECONE_API")
openai_api_key = os.getenv("OPENAI_API_KEY")

# Pinecone API 초기화
pc = Pinecone(api_key=pc_api)

client = OpenAI()

# index 설정
index_name = "data-search-chatbot"
index = pc.Index(index_name)

# Ollama 임베딩 모델 초기화
# EMBEDDING_MODEL = "nomic-embed-text"
EMBEDDING_MODEL = "text-embedding-3-large" # 3072

def query_pinecone(query_text, top_k=5):
    """Pinecone에 쿼리하여 유사한 데이터를 검색."""
    try:
        # Ollama로 쿼리 텍스트의 임베딩 생성
        # embedding_response = ollama.embeddings(
        #     model=EMBEDDING_MODEL,
        #     prompt=query_text
        # )

        # query_embedding = embedding_response["embedding"]

# Openai
        embedding_response = client.embeddings.create(
            input=query_text,
            model=EMBEDDING_MODEL
        )

        query_embedding = embedding_response.data[0].embedding
        # Pinecone에 쿼리 실행
        query_results = index.query(
            vector=query_embedding,
            top_k=top_k,
            include_metadata=True
        )

        print(f"\n쿼리: {query_text}")
        print(f"결과: (Top {top_k})")
        for match in query_results["matches"]:
            print(f" - 제목: {match['metadata']['title']}")
            print(f"   유사도 점수: {match['score']}")
            print(f"   URL: {match['metadata'].get('url', 'N/A')}")
            print(f"   설명: {match['metadata'].get('comprehensive_description', 'N/A')}\n")

    except Exception as e:
        print(f"Error querying Pinecone: {e}")

if __name__ == "__main__":
    # 테스트 쿼리
    query_text = "LLM 학습을 위한 데이터가 필요해"
    query_pinecone(query_text)
