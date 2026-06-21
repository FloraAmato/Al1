"""Good schemas."""
from typing import Optional
from decimal import Decimal
from pydantic import BaseModel, UUID4, Field, ConfigDict


class GoodBase(BaseModel):
    """Base good schema."""
    name: str
    estimated_value: Decimal = Field(..., ge=0, decimal_places=4)
    indivisible: bool = False


class GoodCreate(GoodBase):
    """Good creation schema."""
    dispute_id: UUID4


class GoodUpdate(BaseModel):
    """Good update schema."""
    name: Optional[str] = None
    estimated_value: Optional[Decimal] = Field(default=None, ge=0, decimal_places=4)
    indivisible: Optional[bool] = None


class GoodResponse(GoodBase):
    """Good response schema."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID4
    dispute_id: UUID4


class BidBase(BaseModel):
    """Base bid schema."""
    bid_value: Decimal = Field(..., ge=0, decimal_places=4)


class BidCreate(BidBase):
    """Bid creation schema."""
    agent_id: UUID4
    good_id: UUID4
    dispute_id: UUID4


class BidUpdate(BidBase):
    """Bid update schema."""
    pass


class BidResponse(BidBase):
    """Bid response schema."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID4
    agent_id: UUID4
    good_id: UUID4
    dispute_id: UUID4


class RateBase(BaseModel):
    """Base rate schema."""
    rate_value: int = Field(..., ge=1, le=5)


class RateCreate(RateBase):
    """Rate creation schema."""
    agent_id: UUID4
    good_id: UUID4
    dispute_id: UUID4


class RateUpdate(RateBase):
    """Rate update schema."""
    pass


class RateResponse(RateBase):
    """Rate response schema."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID4
    agent_id: UUID4
    good_id: UUID4
    dispute_id: UUID4
