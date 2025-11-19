"""
Dispute model.
"""
import enum
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Enum, Float, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from app.db.session import Base


class DisputeStatus(str, enum.Enum):
    """Dispute status workflow."""
    SETTING_UP = "setting_up"
    BIDDING = "bidding"
    FINALIZING = "finalizing"
    FINALIZED = "finalized"
    REJECTED = "rejected"


class DisputeResolutionMethod(str, enum.Enum):
    """Dispute resolution method."""
    RATINGS = "ratings"
    BIDS = "bids"


class Dispute(Base):
    """Dispute model - the central entity for fair division."""

    __tablename__ = "disputes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    name = Column(String, nullable=False)
    status = Column(Enum(DisputeStatus), default=DisputeStatus.SETTING_UP, nullable=False, index=True)
    resolution_method = Column(Enum(DisputeResolutionMethod), default=DisputeResolutionMethod.BIDS, nullable=False)

    # Bounds percentage for bid constraints (0.0 to 1.0, stored as decimal)
    bounds_percentage = Column(Float, default=0.25, nullable=False)

    # Rating weight for rating-based resolution (default 1.1)
    rating_weight = Column(Float, default=1.1, nullable=False)

    # Blockchain anchor ID
    block_id = Column(String, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    owner = relationship("User", back_populates="owned_disputes", foreign_keys=[owner_id])
    agents = relationship("Agent", back_populates="dispute", cascade="all, delete-orphan")
    goods = relationship("Good", back_populates="dispute", cascade="all, delete-orphan")
    agent_utilities = relationship("AgentUtility", back_populates="dispute", cascade="all, delete-orphan")
    restricted_assignments = relationship("RestrictedAssignment", back_populates="dispute", cascade="all, delete-orphan")

    @property
    def agents_share_of_entitlement(self) -> float:
        """Calculate the default share of entitlement for agents without custom share."""
        if not self.agents:
            return 1.0

        total_custom_share = sum(
            agent.share_of_entitlement
            for agent in self.agents
            if agent.share_of_entitlement > 0
        )
        num_agents_without_custom = sum(
            1 for agent in self.agents if agent.share_of_entitlement == 0
        )

        remaining_share = 1.0 - total_custom_share
        if remaining_share >= 0 and num_agents_without_custom > 0:
            return remaining_share / num_agents_without_custom
        return 0.0

    @property
    def dispute_budget(self) -> float:
        """Calculate total budget including bounds."""
        if not self.goods:
            return 0.0
        goods_value_sum = sum(float(good.estimated_value) for good in self.goods)
        return goods_value_sum + (goods_value_sum * self.bounds_percentage)
