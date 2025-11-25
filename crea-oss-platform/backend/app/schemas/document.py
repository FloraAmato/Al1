"""Document schemas for API validation."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class DocumentBase(BaseModel):
    """Base document schema."""
    title: str
    source: Optional[str] = None
    content_type: str = "text/plain"
    category: Optional[str] = None


class DocumentCreate(DocumentBase):
    """Schema for creating a document."""
    content: str


class DocumentUpload(BaseModel):
    """Schema for uploading a document."""
    title: str
    category: Optional[str] = None
    # file content is handled separately in multipart upload


class DocumentRead(DocumentBase):
    """Schema for reading document data."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
