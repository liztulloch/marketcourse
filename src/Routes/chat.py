import time

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
    print("CHAT API HIT:", request.message)

    started = time.perf_counter()

    try:
        result = rag_service.answer(request.message)

        result["elapsed_seconds"] = round(
            time.perf_counter() - started,
            2
        )

        return result

    except Exception as e:
        print("CHAT ERROR:", e)

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
