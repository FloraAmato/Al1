"""Dispute and related schemas for API validation."""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict

from app.models.dispute import DisputeStatus, DisputeResolutionMethod
from app.models.agent import ValidatedSteps


# Agent schemas
class AgentBase(BaseModel):
    """Base agent schema."""
    email: str
    name: str
    share_of_entitlement: float = 0.0


class AgentCreate(AgentBase):
    """Schema for creating an agent."""
    pass


class AgentRead(AgentBase):
    """Schema for reading agent data."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    dispute_id: int
    validated: ValidatedSteps


# Good schemas
class GoodBase(BaseModel):
    """Base good schema."""
    name: str
    estimated_value: float
    indivisible: bool = False


class GoodCreate(GoodBase):
    """Schema for creating a good."""
    pass


class GoodRead(GoodBase):
    """Schema for reading good data."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    dispute_id: int


# Dispute schemas
class DisputeBase(BaseModel):
    """Base dispute schema."""
    name: str
    resolution_method: DisputeResolutionMethod = DisputeResolutionMethod.RATINGS
    bounds_percentage: float = 0.25
    rating_weight: float = 1.1


class DisputeCreate(DisputeBase):
    """Schema for creating a dispute."""
    agents: List[AgentCreate] = []
    goods: List[GoodCreate] = []


class DisputeUpdate(BaseModel):
    """Schema for updating a dispute."""
    name: Optional[str] = None
    status: Optional[DisputeStatus] = None
    resolution_method: Optional[DisputeResolutionMethod] = None
    bounds_percentage: Optional[float] = None
    rating_weight: Optional[float] = None


class DisputeRead(DisputeBase):
    """Schema for reading dispute data."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    owner_id: int
    status: DisputeStatus
    created_at: datetime
    updated_at: datetime
    agents: List[AgentRead] = []
    goods: List[GoodRead] = []
