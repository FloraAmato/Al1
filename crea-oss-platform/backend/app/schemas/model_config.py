"""Model configuration schemas for API validation."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict

from app.models.model_config import ModelBackendType


class ModelConfigBase(BaseModel):
    """Base model config schema."""
    name: str
    model_id: str
    backend_type: ModelBackendType
    endpoint_url: Optional[str] = None
    is_active: bool = True
    is_default: bool = False
    is_finetuned: bool = False
    base_model_id: Optional[str] = None
    description: Optional[str] = None


class ModelConfigCreate(ModelConfigBase):
    """Schema for creating a model config."""
    pass


class ModelConfigUpdate(BaseModel):
    """Schema for updating a model config."""
    name: Optional[str] = None
    is_active: Optional[bool] = None
    is_default: Optional[bool] = None
    endpoint_url: Optional[str] = None
    description: Optional[str] = None


class ModelConfigRead(ModelConfigBase):
    """Schema for reading model config data."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
