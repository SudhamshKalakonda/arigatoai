import os
import json
import pickle
import hashlib
from rank_bm25 import BM25Okapi
from dotenv import load_dotenv

load_dotenv()

BM25_INDEX_PATH = "data/bm25_index.pkl"
BM25_DOCS_PATH = "data/bm25_docs.json"

_bm25 = None
_docs = []

def tokenize(text: str) -> list[str]:
    return text.lower().split()

def build_index(chunks: list[dict]) -> None:
    global _bm25, _docs
    _docs = [{"text": c["text"], "metadata": c["metadata"]} for c in chunks]
    tokenized = [tokenize(d["text"]) for d in _docs]
    _bm25 = BM25Okapi(tokenized)

    with open(BM25_INDEX_PATH, "wb") as f:
        pickle.dump(_bm25, f)
    with open(BM25_DOCS_PATH, "w") as f:
        json.dump(_docs, f)

    print(f"BM25 index built with {len(_docs)} documents")

def load_index() -> bool:
    global _bm25, _docs
    if os.path.exists(BM25_INDEX_PATH) and os.path.exists(BM25_DOCS_PATH):
        with open(BM25_INDEX_PATH, "rb") as f:
            _bm25 = pickle.load(f)
        with open(BM25_DOCS_PATH, "r") as f:
            _docs = json.load(f)
        print(f"BM25 index loaded with {len(_docs)} documents")
        return True
    return False

def search_bm25(query: str, top_k: int = 5) -> list[dict]:
    global _bm25, _docs
    if _bm25 is None:
        if not load_index():
            return []

    tokenized_query = tokenize(query)
    scores = _bm25.get_scores(tokenized_query)

    results = []
    for i, score in enumerate(scores):
        if score > 0:
            results.append({
                "text": _docs[i]["text"],
                "metadata": _docs[i]["metadata"],
                "bm25_score": float(score)
            })

    results.sort(key=lambda x: x["bm25_score"], reverse=True)
    return results[:top_k]

def add_to_index(chunks: list[dict]) -> None:
    global _bm25, _docs
    load_index()
    new_docs = [{"text": c["text"], "metadata": c["metadata"]} for c in chunks]
    _docs.extend(new_docs)
    tokenized = [tokenize(d["text"]) for d in _docs]
    _bm25 = BM25Okapi(tokenized)

    with open(BM25_INDEX_PATH, "wb") as f:
        pickle.dump(_bm25, f)
    with open(BM25_DOCS_PATH, "w") as f:
        json.dump(_docs, f)

    print(f"BM25 index updated: {len(_docs)} total documents")