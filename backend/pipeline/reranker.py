from flashrank import Ranker, RerankRequest
from typing import List, Dict

_ranker = None

def get_ranker():
    global _ranker
    if _ranker is None:
        print("Loading re-ranker model...")
        _ranker = Ranker(model_name="ms-marco-MiniLM-L-12-v2")
        print("Re-ranker loaded!")
    return _ranker

def rerank(query: str, chunks: List[Dict], top_k: int = 3) -> List[Dict]:
    if not chunks:
        return []

    ranker = get_ranker()

    passages = []
    for i, chunk in enumerate(chunks):
        text = chunk.get("metadata", {}).get("text", "")
        if not text:
            text = chunk.get("text", "")
        passages.append({"id": str(i), "text": text[:512]})

    request = RerankRequest(query=query, passages=passages)
    results = ranker.rerank(request)

    scored_chunks = []
    for result in results:
        idx = int(result["id"])
        if idx < len(chunks):
            chunk_copy = dict(chunks[idx])
            chunk_copy["rerank_score"] = float(result["score"])
            scored_chunks.append(chunk_copy)

    scored_chunks.sort(key=lambda x: x["rerank_score"], reverse=True)
    return scored_chunks[:top_k]
