import os
import uuid
import time
from dotenv import load_dotenv
from groq import Groq
from langfuse import Langfuse, observe
from pipeline.pinecone_client import hybrid_search
from pipeline.reranker import rerank
from pipeline.compressor import compress_chunks
from pipeline.query_rewriter import rewrite_query
from pipeline.memory import get_session_history, add_to_session
from pipeline.embedder import get_embedding
from database.registry import log_query, init_db

load_dotenv()
init_db()

groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
langfuse = Langfuse(
    public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
    secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
    host=os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")
)

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

@observe()
def answer_question(question: str, firm_id: str = "arigato", session_id: str = "default") -> dict:

    start_time = time.time()
    query_id = str(uuid.uuid4())

    # Step 1 — Rewrite vague queries
    search_query = rewrite_query(question)

    # Step 2 — Hybrid search
    with langfuse.start_as_current_observation(
        name="hybrid_search",
        as_type="retriever",
        input={"query": search_query}
    ):
        matches = hybrid_search(query=search_query, top_k=10)
        langfuse.update_current_span(output={"matches": len(matches)})

    if not matches:
        return {
            "answer": "I don't have enough information on this. Please consult your CA directly.",
            "sources": [],
            "confidence": 0.0,
            "cached": False
        }

    # Step 3 — Re-rank
    with langfuse.start_as_current_observation(
        name="rerank",
        as_type="span",
        input={"chunks": len(matches)}
    ):
        reranked = rerank(query=question, chunks=matches, top_k=3)
        langfuse.update_current_span(output={"reranked": len(reranked)})

    # Step 4 — Contextual compression
    compressed = compress_chunks(query=search_query, chunks=reranked, max_sentences=4)

    # Step 5 — Build context
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

    # Step 6 — Load session memory
    history = get_session_history(session_id)

    # Step 7 — Build messages
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.extend(history)
    messages.append({
        "role": "user",
        "content": f"Context:\n{context}\n\nQuestion: {question}"
    })

    # Step 8 — Generate answer with Groq
    with langfuse.start_as_current_observation(
        name="groq_generation",
        as_type="generation",
        model="llama-3.3-70b-versatile",
        input=messages
    ):
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0.1,
            max_tokens=500
        )
        answer = response.choices[0].message.content
        langfuse.update_current_generation(
            output=answer,
            usage_details={
                "input": response.usage.prompt_tokens,
                "output": response.usage.completion_tokens
            }
        )

    elapsed_ms = int((time.time() - start_time) * 1000)

    result = {
        "answer": answer,
        "sources": sources[:3],
        "confidence": round(avg_score, 4),
        "cached": False
    }

    # Step 9 — Save to session memory
    add_to_session(session_id, question, answer)

    # Step 10 — Log to SQLite
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

    # Step 11 — Update Langfuse trace
    langfuse.set_current_trace_io(
        input={"question": question},
        output={
            "answer": answer,
            "confidence": round(avg_score, 4),
            "latency_ms": elapsed_ms,
            "sources": sources[:3]
        }
    )

    return result
