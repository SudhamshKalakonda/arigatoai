import os
from dotenv import load_dotenv
from pinecone import Pinecone
from pipeline.embedder import get_embeddings_batch
from pipeline.chunker import Chunk

load_dotenv()

_client = None
_index = None

def get_index():
    global _client, _index
    if _index is None:
        _client = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
        _index = _client.Index(os.getenv("PINECONE_INDEX_NAME"))
    return _index

def upsert_chunks(chunks: list[Chunk]):
    if not chunks:
        print("No chunks to upsert")
        return

    index = get_index()
    total_upserted = 0
    embed_batch_size = 50  # Stay under OpenAI 300k token limit
    pinecone_batch_size = 100  # Pinecone recommended batch size

    all_vectors = []

    for i in range(0, len(chunks), embed_batch_size):
        batch = chunks[i:i + embed_batch_size]
        texts = [c.text for c in batch]
        embeddings = get_embeddings_batch(texts)

        for chunk, embedding in zip(batch, embeddings):
            all_vectors.append({
                "id": chunk.chunk_id,
                "values": embedding,
                "metadata": {
                    **chunk.metadata,
                    "text": chunk.text
                }
            })
        print(f"Embedded {min(i + embed_batch_size, len(chunks))}/{len(chunks)} chunks")

    for i in range(0, len(all_vectors), pinecone_batch_size):
        batch = all_vectors[i:i + pinecone_batch_size]
        index.upsert(vectors=batch)
        total_upserted += len(batch)
        print(f"Upserted {total_upserted}/{len(all_vectors)} vectors to Pinecone")

    print(f"Done. Total vectors upserted: {total_upserted}")

def query_vectors(query_embedding: list[float], top_k: int = 10, filter: dict = None):
    index = get_index()
    results = index.query(
        vector=query_embedding,
        top_k=top_k,
        include_metadata=True,
        filter=filter
    )
    return results["matches"]
