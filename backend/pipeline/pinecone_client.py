import os
import hashlib
from dotenv import load_dotenv
from pinecone import Pinecone
from pipeline.embedder import get_embeddings_batch, get_embedding
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
    embed_batch_size = 50
    pinecone_batch_size = 100
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
    # Convert ScoredVector objects to plain dicts
    matches = []
    for m in results["matches"]:
        matches.append({
            "id": m["id"],
            "score": m["score"],
            "metadata": m["metadata"]
        })
    return matches

def hybrid_search(query: str, top_k: int = 5, firm_id: str = None) -> list:
    from pipeline.bm25_index import search_bm25

    # Step 1 — Vector search
    query_embedding = get_embedding(query)
    filter_dict = {"firm_id": firm_id} if firm_id else None
    vector_results = query_vectors(
        query_embedding=query_embedding,
        top_k=top_k * 2,
        filter=filter_dict
    )

    # Step 2 — BM25 keyword search
    bm25_results = search_bm25(query, top_k=top_k * 2)

    # Step 3 — Reciprocal Rank Fusion
    scores = {}

    for rank, result in enumerate(vector_results):
        doc_id = result["id"]
        scores[doc_id] = scores.get(doc_id, 0) + 1 / (rank + 1)

    for rank, result in enumerate(bm25_results):
        doc_id = hashlib.md5(result["text"][:50].encode()).hexdigest()
        scores[doc_id] = scores.get(doc_id, 0) + 1 / (rank + 1)

    # Step 4 — Sort by combined score
    sorted_ids = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_k]
    top_ids = {doc_id for doc_id, _ in sorted_ids}

    # Step 5 — Build final results from vector results first
    final_results = [r for r in vector_results if r["id"] in top_ids]

    # Fill remaining slots from BM25 if needed
    if len(final_results) < top_k:
        for r in bm25_results:
            if len(final_results) >= top_k:
                break
            bm25_id = hashlib.md5(r["text"][:50].encode()).hexdigest()
            if bm25_id not in {res["id"] for res in final_results}:
                final_results.append({
                    "id": bm25_id,
                    "score": r["bm25_score"] / 10,
                    "metadata": {**r["metadata"], "text": r["text"]}
                })

    return final_results[:top_k]
