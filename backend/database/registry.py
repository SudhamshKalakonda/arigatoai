import sqlite3
import json
import os
from datetime import datetime
from typing import Optional

DB_PATH = "database/arigatoai.db"

def get_connection() -> sqlite3.Connection:
    os.makedirs("database", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS documents (
            id              TEXT PRIMARY KEY,
            filename        TEXT NOT NULL,
            title           TEXT,
            source_url      TEXT,
            source_type     TEXT DEFAULT 'pdf',
            category        TEXT DEFAULT 'General',
            credibility     REAL DEFAULT 1.0,
            firm_id         TEXT DEFAULT 'arigato',
            version         INTEGER DEFAULT 1,
            status          TEXT DEFAULT 'indexed',
            valid_from      TEXT,
            expires_at      TEXT,
            chunk_count     INTEGER DEFAULT 0,
            indexed_at      TEXT,
            last_verified   TEXT
        );

        CREATE TABLE IF NOT EXISTS chunks (
            chunk_id        TEXT PRIMARY KEY,
            doc_id          TEXT,
            text            TEXT,
            category        TEXT,
            subcategory     TEXT,
            pinecone_id     TEXT,
            retrieval_count INTEGER DEFAULT 0,
            quality_score   REAL DEFAULT 1.0,
            created_at      TEXT,
            FOREIGN KEY (doc_id) REFERENCES documents(id)
        );

        CREATE TABLE IF NOT EXISTS queries (
            id              TEXT PRIMARY KEY,
            session_id      TEXT,
            question        TEXT NOT NULL,
            rewritten_query TEXT,
            answer          TEXT,
            confidence      REAL,
            cached          INTEGER DEFAULT 0,
            latency_ms      INTEGER,
            sources         TEXT,
            category        TEXT,
            firm_id         TEXT DEFAULT 'arigato',
            created_at      TEXT
        );

        CREATE TABLE IF NOT EXISTS feedback (
            id              TEXT PRIMARY KEY,
            query_id        TEXT,
            rating          INTEGER,
            comment         TEXT,
            created_at      TEXT,
            FOREIGN KEY (query_id) REFERENCES queries(id)
        );

        CREATE INDEX IF NOT EXISTS idx_documents_status ON documents(status);
        CREATE INDEX IF NOT EXISTS idx_documents_category ON documents(category);
        CREATE INDEX IF NOT EXISTS idx_chunks_doc_id ON chunks(doc_id);
        CREATE INDEX IF NOT EXISTS idx_queries_session ON queries(session_id);
        CREATE INDEX IF NOT EXISTS idx_queries_created ON queries(created_at);
        CREATE INDEX IF NOT EXISTS idx_feedback_query ON feedback(query_id);
    """)

    conn.commit()
    conn.close()
    print("Database initialized successfully!")

# ─── DOCUMENT REGISTRY ───────────────────────────────────────────

def document_exists(doc_id: str) -> bool:
    conn = get_connection()
    result = conn.execute(
        "SELECT id FROM documents WHERE id = ?", (doc_id,)
    ).fetchone()
    conn.close()
    return result is not None

def register_document(
    doc_id: str,
    filename: str,
    title: str,
    source_url: str,
    source_type: str,
    category: str,
    credibility: float,
    firm_id: str,
    chunk_count: int,
    valid_from: str = None,
    expires_at: str = None,
    version: int = 1,
) -> None:
    conn = get_connection()

    # Check if document exists — if yes, supersede old version
    existing = conn.execute(
        "SELECT id, version FROM documents WHERE filename = ? AND firm_id = ? AND status = 'indexed'",
        (filename, firm_id)
    ).fetchone()

    if existing:
        conn.execute(
            "UPDATE documents SET status = 'superseded' WHERE id = ?",
            (existing["id"],)
        )
        version = existing["version"] + 1
        print(f"Superseded old version of {filename} (was v{existing['version']})")

    conn.execute("""
        INSERT OR REPLACE INTO documents
        (id, filename, title, source_url, source_type, category,
         credibility, firm_id, version, status, valid_from,
         expires_at, chunk_count, indexed_at, last_verified)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'indexed', ?, ?, ?, ?, ?)
    """, (
        doc_id, filename, title, source_url, source_type, category,
        credibility, firm_id, version, valid_from, expires_at,
        chunk_count,
        datetime.now().isoformat(),
        datetime.now().isoformat()
    ))

    conn.commit()
    conn.close()
    print(f"Registered: {filename} v{version} ({chunk_count} chunks)")

def register_chunk(
    chunk_id: str,
    doc_id: str,
    text: str,
    category: str,
    subcategory: str = None,
    pinecone_id: str = None,
) -> None:
    conn = get_connection()
    conn.execute("""
        INSERT OR REPLACE INTO chunks
        (chunk_id, doc_id, text, category, subcategory, pinecone_id, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        chunk_id, doc_id, text, category, subcategory,
        pinecone_id or chunk_id,
        datetime.now().isoformat()
    ))
    conn.commit()
    conn.close()

def get_all_documents(firm_id: str = None, status: str = "indexed") -> list:
    conn = get_connection()
    if firm_id:
        rows = conn.execute(
            "SELECT * FROM documents WHERE firm_id = ? AND status = ? ORDER BY indexed_at DESC",
            (firm_id, status)
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM documents WHERE status = ? ORDER BY indexed_at DESC",
            (status,)
        ).fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_document(doc_id: str) -> Optional[dict]:
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM documents WHERE id = ?", (doc_id,)
    ).fetchone()
    conn.close()
    return dict(row) if row else None

# ─── QUERY LOGGING ───────────────────────────────────────────────

def log_query(
    query_id: str,
    session_id: str,
    question: str,
    rewritten_query: str,
    answer: str,
    confidence: float,
    cached: bool,
    latency_ms: int,
    sources: list,
    category: str = "General",
    firm_id: str = "arigato"
) -> None:
    conn = get_connection()
    conn.execute("""
        INSERT INTO queries
        (id, session_id, question, rewritten_query, answer, confidence,
         cached, latency_ms, sources, category, firm_id, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        query_id, session_id, question, rewritten_query, answer,
        confidence, int(cached), latency_ms,
        json.dumps(sources), category, firm_id,
        datetime.now().isoformat()
    ))
    conn.commit()
    conn.close()

# ─── FEEDBACK ────────────────────────────────────────────────────

def log_feedback(
    feedback_id: str,
    query_id: str,
    rating: int,
    comment: str = None
) -> None:
    conn = get_connection()
    conn.execute("""
        INSERT INTO feedback (id, query_id, rating, comment, created_at)
        VALUES (?, ?, ?, ?, ?)
    """, (
        feedback_id, query_id, rating, comment,
        datetime.now().isoformat()
    ))
    conn.commit()
    conn.close()

# ─── ANALYTICS ───────────────────────────────────────────────────

def get_analytics(firm_id: str = "arigato") -> dict:
    conn = get_connection()

    total_queries = conn.execute(
        "SELECT COUNT(*) as count FROM queries WHERE firm_id = ?",
        (firm_id,)
    ).fetchone()["count"]

    avg_confidence = conn.execute(
        "SELECT AVG(confidence) as avg FROM queries WHERE firm_id = ? AND cached = 0",
        (firm_id,)
    ).fetchone()["avg"] or 0

    cache_hits = conn.execute(
        "SELECT COUNT(*) as count FROM queries WHERE firm_id = ? AND cached = 1",
        (firm_id,)
    ).fetchone()["count"]

    low_confidence = conn.execute(
        """SELECT question, confidence FROM queries
           WHERE firm_id = ? AND confidence < 0.5 AND cached = 0
           ORDER BY created_at DESC LIMIT 10""",
        (firm_id,)
    ).fetchall()

    top_questions = conn.execute(
        """SELECT question, COUNT(*) as count FROM queries
           WHERE firm_id = ?
           GROUP BY question ORDER BY count DESC LIMIT 10""",
        (firm_id,)
    ).fetchall()

    total_docs = conn.execute(
        "SELECT COUNT(*) as count FROM documents WHERE firm_id = ? AND status = 'indexed'",
        (firm_id,)
    ).fetchone()["count"]

    conn.close()

    return {
        "total_queries": total_queries,
        "avg_confidence": round(avg_confidence, 2),
        "cache_hit_rate": round(cache_hits / max(total_queries, 1) * 100, 1),
        "total_documents": total_docs,
        "low_confidence_questions": [dict(r) for r in low_confidence],
        "top_questions": [dict(r) for r in top_questions]
    }

def get_data_gaps(firm_id: str = "arigato") -> list:
    """Find topics with consistently low confidence — data gaps."""
    conn = get_connection()
    gaps = conn.execute(
        """SELECT question, AVG(confidence) as avg_conf, COUNT(*) as count
           FROM queries
           WHERE firm_id = ? AND cached = 0 AND confidence < 0.5
           GROUP BY question
           HAVING count >= 2
           ORDER BY avg_conf ASC LIMIT 20""",
        (firm_id,)
    ).fetchall()
    conn.close()
    return [dict(g) for g in gaps]

if __name__ == "__main__":
    init_db()