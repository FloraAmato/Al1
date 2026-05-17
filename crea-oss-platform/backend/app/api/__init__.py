"""API router configuration."""
from fastapi import APIRouter
from app.api.routes import chat, disputes, documents, models

api_router = APIRouter()

# Include all route modules
api_router.include_router(chat.router)
api_router.include_router(disputes.router)
api_router.include_router(documents.router)
api_router.include_router(models.router)

__all__ = ["api_router"]
