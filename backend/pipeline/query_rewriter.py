import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

_client = None

def get_client():
    global _client
    if _client is None:
        _client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    return _client

REWRITE_PROMPT = """You are a query expansion expert for an Indian tax and compliance chatbot.

Your job is to rewrite vague or short user questions into detailed, keyword-rich search queries.

Rules:
- Expand abbreviations (80C → Section 80C Income Tax, GST → Goods and Services Tax)
- Add relevant Indian tax terminology
- Keep it as ONE clear question
- Maximum 50 words
- Do NOT answer the question, just rewrite it
- If the question is already clear and detailed, return it as-is

Examples:
Input: "80C limit?"
Output: "What is the maximum deduction limit under Section 80C of the Income Tax Act for investments in PPF ELSS life insurance and other specified instruments?"

Input: "gstr3b date"  
Output: "What is the due date for filing GSTR-3B return under GST for monthly taxpayers?"

Input: "tds on rent"
Output: "What is the TDS rate on rent payment under Section 194I of the Income Tax Act for land building and machinery?"

Input: "How do I file ITR-1 online step by step?"
Output: "How do I file ITR-1 online step by step?"

Now rewrite this query. Return ONLY the rewritten query, nothing else:"""

def rewrite_query(query: str) -> str:
    """
    Rewrites a vague query into a detailed search-optimized query.
    Falls back to original query if rewriting fails.
    """
    if len(query.split()) >= 10:
        return query

    try:
        client = get_client()
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "user", "content": f"{REWRITE_PROMPT}\n\nQuery: {query}"}
            ],
            temperature=0.1,
            max_tokens=100
        )
        rewritten = response.choices[0].message.content.strip()
        print(f"Query rewritten: '{query}' → '{rewritten}'")
        return rewritten
    except Exception as e:
        print(f"Query rewrite failed, using original: {e}")
        return query