from fastapi import APIRouter, UploadFile, File, Form, BackgroundTasks
from pydantic import BaseModel
import uuid
from api.rag import answer_question
from pipeline.pinecone_client import get_index
from pipeline.semantic_cache import get_cache_stats
from pipeline.memory import get_memory_stats

router = APIRouter()

class AskRequest(BaseModel):
    question: str
    firm_id: str = "arigato"
    session_id: str = "default"

class AskResponse(BaseModel):
    answer: str
    sources: list[str]
    confidence: float
    cached: bool = False

@router.post("/ask", response_model=AskResponse)
def ask(request: AskRequest):
    result = answer_question(
        question=request.question,
        firm_id=request.firm_id,
        session_id=request.session_id
    )
    return AskResponse(**result)

def process_upload_background(
    file_bytes: bytes,
    filename: str,
    title: str,
    firm_id: str,
    job_id: str
):
    """Background task — runs after API returns response."""
    from pipeline.indexing_pipeline import index_file_bytes
    from database.registry import get_connection

    # Update status to processing
    conn = get_connection()
    conn.execute(
        "UPDATE documents SET status = 'processing' WHERE filename = ? AND firm_id = ?",
        (filename, firm_id)
    )
    conn.commit()
    conn.close()

    try:
        result = index_file_bytes(
            file_bytes=file_bytes,
            filename=filename,
            title=title,
            firm_id=firm_id
        )
        print(f"Background indexing complete: {filename} — {result['status']}")
    except Exception as e:
        print(f"Background indexing failed: {filename} — {e}")
        conn = get_connection()
        conn.execute(
            "UPDATE documents SET status = 'failed' WHERE filename = ? AND firm_id = ?",
            (filename, firm_id)
        )
        conn.commit()
        conn.close()

@router.post("/upload")
async def upload_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    title: str = Form(default=None),
    firm_id: str = Form(default="arigato")
):
    from pipeline.extractor import is_supported
    if not is_supported(file.filename):
        return {"error": f"Unsupported format. Supported: PDF, DOCX, TXT, XLSX, CSV"}

    file_bytes = await file.read()
    job_id = str(uuid.uuid4())

    # Add to background tasks — returns immediately
    background_tasks.add_task(
        process_upload_background,
        file_bytes,
        file.filename,
        title or file.filename,
        firm_id,
        job_id
    )

    return {
        "message": f"Upload received — {file.filename} is being indexed in the background",
        "job_id": job_id,
        "filename": file.filename,
        "status": "processing"
    }

@router.get("/upload/status/{filename}")
def upload_status(filename: str, firm_id: str = "arigato"):
    """Check if a document has finished indexing."""
    from database.registry import get_connection
    conn = get_connection()
    doc = conn.execute(
        "SELECT filename, status, chunk_count, indexed_at FROM documents WHERE filename = ? AND firm_id = ?",
        (filename, firm_id)
    ).fetchone()
    conn.close()

    if not doc:
        return {"status": "not_found", "filename": filename}

    return {
        "filename": doc["filename"],
        "status": doc["status"],
        "chunk_count": doc["chunk_count"],
        "indexed_at": doc["indexed_at"]
    }

@router.get("/stats")
def stats():
    from database.registry import get_analytics, get_data_gaps
    index = get_index()
    s = index.describe_index_stats()
    analytics = get_analytics()
    gaps = get_data_gaps()
    return {
        "total_vectors": s["total_vector_count"],
        "index_fullness": s["index_fullness"],
        "analytics": analytics,
        "data_gaps": gaps
    }

@router.post("/feedback")
def feedback(request: dict):
    from database.registry import log_feedback
    log_feedback(
        feedback_id=str(uuid.uuid4()),
        query_id=request.get("query_id"),
        rating=request.get("rating"),
        comment=request.get("comment")
    )
    return {"message": "Feedback recorded"}

@router.get("/documents")
def list_documents(firm_id: str = "arigato"):
    from database.registry import get_all_documents
    docs = get_all_documents(firm_id=firm_id)
    return {"documents": docs, "total": len(docs)}

@router.delete("/documents/{doc_id}")
def delete_document(doc_id: str):
    from database.registry import get_connection
    conn = get_connection()
    chunks = conn.execute(
        "SELECT chunk_id FROM chunks WHERE doc_id = ?", (doc_id,)
    ).fetchall()
    chunk_ids = [c["chunk_id"] for c in chunks]
    if chunk_ids:
        index = get_index()
        index.delete(ids=chunk_ids)
    conn.execute("DELETE FROM chunks WHERE doc_id = ?", (doc_id,))
    conn.execute(
        "UPDATE documents SET status = 'deleted' WHERE id = ?", (doc_id,)
    )
    conn.commit()
    conn.close()
    return {
        "message": "Document deleted successfully",
        "doc_id": doc_id,
        "vectors_deleted": len(chunk_ids)
    }