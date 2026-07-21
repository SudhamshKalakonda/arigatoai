import os
import uuid
import time
from dotenv import load_dotenv
from groq import Groq
from pipeline.pinecone_client import hybrid_search
from pipeline.reranker import rerank
from pipeline.compressor import compress_chunks
from pipeline.query_rewriter import rewrite_query
from pipeline.semantic_cache import get_cached, set_cached
from pipeline.memory import get_session_history, add_to_session
from pipeline.embedder import get_embedding
from database.registry import log_query, init_db

load_dotenv()
init_db()

groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

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
6. Always recommend consulting the CA for complex matters
7. Use conversation history to answer follow-up questions"""

def answer_question(question: str, firm_id: str = "arigato", session_id: str = "default") -> dict:

    start_time = time.time()
    query_id = str(uuid.uuid4())

    # Step 0 — Embed question
    question_embedding = get_embedding(question)

    # Step 1 — Check semantic cache
    cached = get_cached(question, question_embedding)
    if cached:
        add_to_session(session_id, question, cached["answer"])
        elapsed_ms = int((time.time() - start_time) * 1000)
        log_query(
            query_id=query_id,
            session_id=session_id,
            question=question,
            rewritten_query=question,
            answer=cached["answer"],
            confidence=cached.get("confidence", 0),
            cached=True,
            latency_ms=elapsed_ms,
            sources=cached.get("sources", []),
            firm_id=firm_id
        )
        return {**cached, "cached": True}

    # Step 2 — Rewrite vague queries
    search_query = rewrite_query(question)

    # Step 3 — Hybrid search
    matches = hybrid_search(query=search_query, top_k=10)

    if not matches:
        return {
            "answer": "I don't have enough information on this. Please consult your CA directly.",
            "sources": [],
            "confidence": 0.0,
            "cached": False
        }

    # Step 4 — Re-rank
    reranked = rerank(query=question, chunks=matches, top_k=3)

    # Step 5 — Contextual compression
    compressed = compress_chunks(query=search_query, chunks=reranked, max_sentences=4)

    # Step 6 — Build context
    context_parts = []
    sources = []

    for match in compressed:
        text = match.get("metadata", {}).get("text", "")
        source_url = match.get("metadata", {}).get("source_url", "")
        if text:
            context_parts.append(text)
        if source_url and source_url not in sources:
            sources.append(source_url)

    if not context_parts:
        return {
            "answer": "I don't have enough information on this. Please consult your CA directly.",
            "sources": [],
            "confidence": 0.0,
            "cached": False
        }

    context = "\n\n".join(context_parts)
    avg_score = sum(m.get("rerank_score", 0) for m in reranked[:3]) / 3

    # Step 7 — Load session memory
    history = get_session_history(session_id)

    # Step 8 — Build messages with history + context
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.extend(history)
    messages.append({
        "role": "user",
        "content": f"Context:\n{context}\n\nQuestion: {question}"
    })

    # Step 9 — Generate answer with Groq
    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
        temperature=0.1,
        max_tokens=500
    )

    answer = response.choices[0].message.content

    result = {
        "answer": answer,
        "sources": sources[:3],
        "confidence": round(avg_score, 4),
        "cached": False
    }

    # Step 10 — Save to session memory + semantic cache
    add_to_session(session_id, question, answer)
    set_cached(question, question_embedding, result)

    # Step 11 — Log query to database
    elapsed_ms = int((time.time() - start_time) * 1000)
    log_query(
        query_id=query_id,
        session_id=session_id,
        question=question,
        rewritten_query=search_query,
        answer=answer,
        confidence=round(avg_score, 4),
        cached=False,
        latency_ms=elapsed_ms,
        sources=sources[:3],
        firm_id=firm_id
    )

    return result