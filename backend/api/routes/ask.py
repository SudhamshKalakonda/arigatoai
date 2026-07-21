from fastapi import APIRouter, UploadFile, File, Form
from pydantic import BaseModel
from api.rag import answer_question
from pipeline.pdf_parser import parse_pdf_bytes
from pipeline.pinecone_client import upsert_chunks, get_index
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

@router.post("/upload")
async def upload_pdf(
    file: UploadFile = File(...),
    title: str = Form(default=None),
    firm_id: str = Form(default="arigato")
):
    from pipeline.extractor import is_supported
    if not is_supported(file.filename):
        return {"error": f"Unsupported format. Supported: PDF, DOCX, TXT, XLSX, CSV"}

    file_bytes = await file.read()

    from pipeline.indexing_pipeline import index_pdf_bytes
    result = index_pdf_bytes(
        file_bytes=file_bytes,
        filename=file.filename,
        title=title or file.filename,
        firm_id=firm_id
    )

    if result["status"] == "skipped":
        return {
            "message": "Document already indexed — skipping duplicate",
            "doc_id": result["doc_id"],
            "status": "skipped"
        }

    if result["status"] == "failed":
        return {"error": result["reason"]}

    stats = get_index().describe_index_stats()
    return {
        "message": f"Successfully indexed {file.filename}",
        "chunks_added": result["chunk_count"],
        "category": result["category"],
        "subcategory": result["subcategory"],
        "total_vectors": stats["total_vector_count"],
        "doc_id": result["doc_id"]
    }

@router.get("/stats")
def stats():
    index = get_index()
    s = index.describe_index_stats()
    cache_stats = get_cache_stats()
    memory_stats = get_memory_stats()
    return {
        "total_vectors": s["total_vector_count"],
        "index_fullness": s["index_fullness"],
        "cache": cache_stats,
        "memory": memory_stats
    }




@router.delete("/documents/{doc_id}")
def delete_document(doc_id: str):
    from database.registry import get_connection
    from pipeline.pinecone_client import get_index

    conn = get_connection()

    # Get chunk IDs to delete from Pinecone
    chunks = conn.execute(
        "SELECT chunk_id FROM chunks WHERE doc_id = ?", (doc_id,)
    ).fetchall()

    chunk_ids = [c["chunk_id"] for c in chunks]

    # Delete from Pinecone
    if chunk_ids:
        index = get_index()
        index.delete(ids=chunk_ids)
        print(f"Deleted {len(chunk_ids)} vectors from Pinecone")

    # Delete from SQLite
    conn.execute("DELETE FROM chunks WHERE doc_id = ?", (doc_id,))
    conn.execute(
        "UPDATE documents SET status = 'deleted' WHERE id = ?", (doc_id,)
    )
    conn.commit()
    conn.close()

    return {
        "message": f"Document deleted successfully",
        "doc_id": doc_id,
        "vectors_deleted": len(chunk_ids)
    }