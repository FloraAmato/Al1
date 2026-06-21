"""Agent schemas."""
from typing import Optional
from pydantic import BaseModel, EmailStr, UUID4, Field, ConfigDict
from app.models.agent import ValidatedSteps


class AgentBase(BaseModel):
    """Base agent schema."""
    email: EmailStr
    share_of_entitlement: Optional[float] = Field(default=0.0, ge=0.0, le=1.0)


class AgentCreate(AgentBase):
    """Agent creation schema."""
    dispute_id: UUID4


class AgentUpdate(BaseModel):
    """Agent update schema."""
    email: Optional[EmailStr] = None
    share_of_entitlement: Optional[float] = Field(default=None, ge=0.0, le=1.0)


class AgentResponse(AgentBase):
    """Agent response schema."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID4
    dispute_id: UUID4
    user_id: Optional[UUID4] = None
    validated: ValidatedSteps
    name: str


class AgentValidation(BaseModel):
    """Agent validation schema."""
    agent_id: UUID4
    validated: ValidatedSteps
