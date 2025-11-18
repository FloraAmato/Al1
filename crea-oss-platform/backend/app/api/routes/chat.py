"""Chat API routes."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_db
from app.schemas.chat import ChatRequest, ChatResponse
from app.services import ChatService

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    db: AsyncSession = Depends(get_async_db),
):
    """
    Send a chat message and get a response.

    Integrates LLM, RAG, and dispute resolution tools.
    """
    # For demo, use a fixed user_id=1 (in production, use auth)
    user_id = 1

    try:
        service = ChatService(db)
        result = await service.chat(
            user_id=user_id,
            session_id=request.session_id,
            message=request.message,
            model_id=request.model_id,
            use_rag=request.use_rag,
            dispute_id=request.dispute_id,
        )

        return ChatResponse(**result)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
