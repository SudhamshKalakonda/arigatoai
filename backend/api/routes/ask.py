from fastapi import APIRouter, UploadFile, File, Form
from pydantic import BaseModel
from api.rag import answer_question
from pipeline.pdf_parser import parse_pdf_bytes
from pipeline.pinecone_client import upsert_chunks, get_index

router = APIRouter()

class AskRequest(BaseModel):
    question: str
    firm_id: str = "arigato"

class AskResponse(BaseModel):
    answer: str
    sources: list[str]
    confidence: float

@router.post("/ask", response_model=AskResponse)
def ask(request: AskRequest):
    result = answer_question(
        question=request.question,
        firm_id=request.firm_id
    )
    return AskResponse(**result)

@router.post("/upload")
async def upload_pdf(
    file: UploadFile = File(...),
    title: str = Form(default=None),
    firm_id: str = Form(default="arigato")
):
    if not file.filename.endswith(".pdf"):
        return {"error": "Only PDF files are supported"}

    file_bytes = await file.read()
    chunks = parse_pdf_bytes(
        file_bytes=file_bytes,
        filename=file.filename,
        title=title or file.filename,
        firm_id=firm_id
    )

    if not chunks:
        return {"error": "No text could be extracted from this PDF"}

    upsert_chunks(chunks)

    stats = get_index().describe_index_stats()

    return {
        "message": f"Successfully uploaded and indexed {file.filename}",
        "chunks_added": len(chunks),
        "total_vectors": stats["total_vector_count"]
    }

@router.get("/stats")
def stats():
    index = get_index()
    s = index.describe_index_stats()
    return {
        "total_vectors": s["total_vector_count"],
        "index_fullness": s["index_fullness"]
    }