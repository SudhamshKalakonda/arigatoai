import os
import json
import time
import numpy as np
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

CACHE_FILE = "data/semantic_cache.json"
SIMILARITY_THRESHOLD = 0.90
CACHE_TTL = 7 * 24 * 60 * 60  # 7 days in seconds

def cosine_similarity(a: list, b: list) -> float:
    a = np.array(a)
    b = np.array(b)
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

def load_cache() -> list:
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r") as f:
            return json.load(f)
    return []

def save_cache(entries: list) -> None:
    os.makedirs("data", exist_ok=True)
    with open(CACHE_FILE, "w") as f:
        json.dump(entries, f)

def purge_expired(entries: list) -> list:
    now = time.time()
    active = [e for e in entries if now - e["timestamp"] < CACHE_TTL]
    if len(active) < len(entries):
        print(f"Purged {len(entries) - len(active)} expired cache entries")
    return active

def get_cached(question: str, question_embedding: list) -> Optional[dict]:
    entries = load_cache()
    entries = purge_expired(entries)
    save_cache(entries)

    best_score = 0.0
    best_entry = None

    for entry in entries:
        score = cosine_similarity(question_embedding, entry["embedding"])
        if score > best_score:
            best_score = score
            best_entry = entry

    if best_score >= SIMILARITY_THRESHOLD and best_entry:
        print(f"Semantic cache hit! Score: {best_score:.4f} | Original: '{best_entry['question'][:50]}'")
        return best_entry["result"]

    print(f"Cache miss. Best score: {best_score:.4f}")
    return None

def set_cached(question: str, question_embedding: list, result: dict) -> None:
    entries = load_cache()
    entries = purge_expired(entries)

    entries.append({
        "question": question,
        "embedding": question_embedding,
        "result": result,
        "timestamp": time.time()
    })

    save_cache(entries)
    print(f"Cached: '{question[:50]}'")

def get_cache_stats() -> dict:
    entries = load_cache()
    entries = purge_expired(entries)
    return {
        "total_cached": len(entries),
        "threshold": SIMILARITY_THRESHOLD,
        "ttl_days": CACHE_TTL / 86400
    }