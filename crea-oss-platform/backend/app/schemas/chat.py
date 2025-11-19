"""Chat schemas for API validation."""
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict

from app.models.conversation import MessageRole


class MessageRead(BaseModel):
    """Schema for reading message data."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    role: MessageRole
    content: str
    metadata: Optional[str] = None
    created_at: datetime


class ChatRequest(BaseModel):
    """Schema for chat request."""
    message: str
    session_id: str
    model_id: Optional[str] = None
    use_rag: bool = True
    dispute_id: Optional[int] = None


class ChatResponse(BaseModel):
    """Schema for chat response."""
    answer: str
    sources: List[Dict[str, Any]] = []
    session_id: str
    model_used: Optional[str] = None


class ConversationRead(BaseModel):
    """Schema for reading conversation data."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    session_id: str
    title: Optional[str]
    model_id: Optional[str]
    created_at: datetime
    updated_at: datetime
    messages: List[MessageRead] = []
