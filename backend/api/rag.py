import os
import asyncio
import time
from dotenv import load_dotenv
from groq import Groq
from pipeline.embedder import get_embedding
from pipeline.pinecone_client import query_vectors

load_dotenv()

groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Simple in-memory cache for frequent queries
_cache = {}
CACHE_TTL = 3600  # 1 hour

SYSTEM_PROMPT = """You are ArigatoAI, a helpful assistant for CA (Chartered Accountant) firms in India.

You answer client questions about:
- Income Tax, ITR filing, tax deadlines
- GST registration, returns, compliance
- EPF, ESI, professional tax
- Company law, MCA compliance

STRICT RULES:
1. Only answer using the provided context
2. If the answer is not in the context, say "I don't have enough information on this. Please consult your CA directly."
3. Always mention the source of your answer
4. Be concise and clear — clients are non-technical
5. Never give wrong information — when unsure, say so
6. Always recommend consulting the CA for complex matters"""

def answer_question(question: str, firm_id: str = "arigato") -> dict:
    # Cache check
    cache_key = question.strip().lower()
    if cache_key in _cache:
        cached_time, cached_result = _cache[cache_key]
        if time.time() - cached_time < CACHE_TTL:
            cached_result["_cached"] = True
            return cached_result

    # Step 1: Embed query
    question_embedding = get_embedding(question)

    # Step 2: Pinecone retrieval
    matches = query_vectors(
        query_embedding=question_embedding,
        top_k=5
    )

    if not matches:
        return {
            "answer": "I don't have enough information on this. Please consult your CA directly.",
            "sources": [],
            "confidence": 0.0
        }

    context_parts = []
    sources = []

    for match in matches:
        text = match["metadata"].get("text", "")
        source_url = match["metadata"].get("source_url", "")
        if text:
            context_parts.append(text)
        if source_url and source_url not in sources:
            # Filter out test/dummy URLs
            if source_url and "test.com" not in source_url:
                sources.append(source_url)

    context = "\n\n".join(context_parts)
    avg_score = sum(m["score"] for m in matches[:3]) / 3

    # Step 3: Groq LLM — switched to 8b-instant for 3x speed
    response = groq_client.chat.completions.create(
        model="llama-3.1-8b-instant",  # was llama-3.3-70b-versatile
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"}
        ],
        temperature=0.1,
        max_tokens=500
    )

    answer = response.choices[0].message.content

    result = {
        "answer": answer,
        "sources": sources[:3],
        "confidence": round(avg_score, 4)
    }

    # Store in cache
    _cache[cache_key] = (time.time(), result)

    return result
