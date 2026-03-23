import os
from dotenv import load_dotenv
from groq import Groq
from pipeline.embedder import get_embedding
from pipeline.pinecone_client import query_vectors

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
    question_embedding = get_embedding(question)

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
            sources.append(source_url)

    context = "\n\n".join(context_parts)
    avg_score = sum(m["score"] for m in matches[:3]) / 3

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
