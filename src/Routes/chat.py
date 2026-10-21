from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from src.Services.rag_service import RAGService

router = APIRouter(
    prefix="/chat",
    tags=["chat"]
)

rag_service = RAGService()


class ChatRequest(BaseModel):
    message: str


@router.post("/")
def chat(request: ChatRequest):
    try:
        return rag_service.answer(request.message)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )