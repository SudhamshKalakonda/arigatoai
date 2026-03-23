from fastapi import APIRouter
from pydantic import BaseModel
from api.rag import answer_question

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