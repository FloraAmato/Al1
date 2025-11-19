"""Solution schemas for API validation."""
from datetime import datetime
from typing import List, Literal, Optional
from pydantic import BaseModel, ConfigDict


class AllocationItemRead(BaseModel):
    """Schema for reading allocation item data."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    agent_id: int
    good_id: int
    amount: float


class SolutionRead(BaseModel):
    """Schema for reading solution data."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    dispute_id: int
    method: str
    objective_value: Optional[float]
    computation_time_ms: Optional[float]
    created_at: datetime
    allocations: List[AllocationItemRead] = []


class SolveRequest(BaseModel):
    """Schema for requesting a solution."""
    method: Literal["maxmin", "nash"] = "maxmin"
