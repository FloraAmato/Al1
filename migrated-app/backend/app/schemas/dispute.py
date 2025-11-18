"""Dispute schemas."""
from typing import List, Optional
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, UUID4, Field, ConfigDict
from app.models.dispute import DisputeStatus, DisputeResolutionMethod


class DisputeBase(BaseModel):
    """Base dispute schema."""
    name: str
    resolution_method: DisputeResolutionMethod = DisputeResolutionMethod.BIDS
    bounds_percentage: Optional[float] = Field(default=0.25, ge=0.0, le=1.0)
    rating_weight: Optional[float] = Field(default=1.1, ge=1.0, le=2.0)


class DisputeCreate(DisputeBase):
    """Dispute creation schema."""
    pass


class DisputeUpdate(BaseModel):
    """Dispute update schema."""
    name: Optional[str] = None
    status: Optional[DisputeStatus] = None
    resolution_method: Optional[DisputeResolutionMethod] = None
    bounds_percentage: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    rating_weight: Optional[float] = Field(default=None, ge=1.0, le=2.0)


class DisputeInDB(DisputeBase):
    """Dispute database schema."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID4
    owner_id: UUID4
    status: DisputeStatus
    block_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class Dispute(DisputeInDB):
    """Dispute response schema."""
    agents: List["AgentResponse"] = []
    goods: List["GoodResponse"] = []


class DisputeListItem(DisputeInDB):
    """Dispute list item schema."""
    agents_count: int = 0
    goods_count: int = 0


# Forward references
from app.schemas.agent import AgentResponse
from app.schemas.good import GoodResponse

Dispute.model_rebuild()
