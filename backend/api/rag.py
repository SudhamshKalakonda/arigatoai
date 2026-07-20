import os
from dotenv import load_dotenv
from groq import Groq
from pipeline.pinecone_client import hybrid_search
from pipeline.reranker import rerank
from pipeline.query_rewriter import rewrite_query
from pipeline.compressor import compress_chunks

load_dotenv()

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
6. Always recommend consulting the CA for complex matters"""

def answer_question(question: str, firm_id: str = "arigato") -> dict:

    search_query = rewrite_query(question)

    # Step 1 — Hybrid search (vector + BM25)
    matches = hybrid_search(query=question, top_k=10)

    if not matches:
        return {
            "answer": "I don't have enough information on this. Please consult your CA directly.",
            "sources": [],
            "confidence": 0.0
        }

    # Step 2 — Re-rank to get top 3 most relevant chunks
    reranked = rerank(query=question, chunks=matches, top_k=3)

    compressed = compress_chunks(query=search_query, chunks=reranked, max_sentences=4)

    # Step 3 — Build context from re-ranked chunks
    context_parts = []
    sources = []

    for match in reranked:
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
            "confidence": 0.0
        }

    context = "\n\n".join(context_parts)
    avg_score = sum(m.get("rerank_score", 0) for m in reranked[:3]) / 3

    # Step 4 — Generate answer with Groq
    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"}
        ],
        temperature=0.1,
        max_tokens=500
    )

    answer = response.choices[0].message.content

    return {
        "answer": answer,
        "sources": sources[:3],
        "confidence": round(avg_score, 4)
    }