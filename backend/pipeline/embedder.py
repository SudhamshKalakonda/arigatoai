import os
import time
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_embedding(text: str) -> list[float]:
    text = text.replace("\n", " ").strip()[:6000]
    for attempt in range(3):
        try:
            response = client.embeddings.create(
                input=text,
                model="text-embedding-3-small"
            )
            return response.data[0].embedding
        except Exception as e:
            if attempt < 2:
                print(f"Embedding retry {attempt+1}/3: {e}")
                time.sleep(2 ** attempt)
            else:
                raise

def get_embeddings_batch(texts: list[str]) -> list[list[float]]:
    texts = [t[:6000].replace("\n", " ").strip() for t in texts]
    for attempt in range(3):
        try:
            response = client.embeddings.create(
                input=texts,
                model="text-embedding-3-small"
            )
            return [item.embedding for item in response.data]
        except Exception as e:
            if attempt < 2:
                print(f"Batch embedding retry {attempt+1}/3: {e}")
                time.sleep(2 ** attempt)
            else:
                raise