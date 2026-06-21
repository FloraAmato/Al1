"""
Agent utility models (Bid and Rate).
"""
import uuid
import math
from sqlalchemy import Column, Integer, Numeric, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from app.db.session import Base


class AgentUtility(Base):
    """Base class for agent utilities (polymorphic)."""

    __tablename__ = "agent_utilities"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    agent_id = Column(UUID(as_uuid=True), ForeignKey("agents.id", ondelete="CASCADE"), nullable=False, index=True)
    good_id = Column(UUID(as_uuid=True), ForeignKey("goods.id", ondelete="CASCADE"), nullable=False, index=True)
    dispute_id = Column(UUID(as_uuid=True), ForeignKey("disputes.id", ondelete="CASCADE"), nullable=False, index=True)

    # Polymorphic discriminator
    type = Column(String(50), nullable=False)

    # Relationships
    agent = relationship("Agent", back_populates="agent_utilities")
    good = relationship("Good", back_populates="agent_utilities")
    dispute = relationship("Dispute", back_populates="agent_utilities")

    __mapper_args__ = {
        "polymorphic_identity": "agent_utility",
        "polymorphic_on": type,
    }


class Bid(AgentUtility):
    """Bid model for bid-based resolution."""

    __tablename__ = "bids"

    id = Column(UUID(as_uuid=True), ForeignKey("agent_utilities.id", ondelete="CASCADE"), primary_key=True)
    bid_value = Column(Numeric(precision=19, scale=4), nullable=False, default=0)

    __mapper_args__ = {
        "polymorphic_identity": "bid",
    }

    __table_args__ = (
        UniqueConstraint("agent_id", "good_id", "dispute_id", name="unique_bid_per_agent_good"),
    )

    def get_lower_bound(self, good_estimated_value: float, bounds_percentage: float) -> float:
        """Calculate lower bound for this bid."""
        return good_estimated_value - (good_estimated_value * bounds_percentage)

    def get_upper_bound(self, good_estimated_value: float, bounds_percentage: float) -> float:
        """Calculate upper bound for this bid."""
        return good_estimated_value + (good_estimated_value * bounds_percentage)

    def calculate_utility(self) -> float:
        """Calculate utility (bid value)."""
        return float(self.bid_value)


class Rate(AgentUtility):
    """Rate model for rating-based resolution."""

    __tablename__ = "rates"

    id = Column(UUID(as_uuid=True), ForeignKey("agent_utilities.id", ondelete="CASCADE"), primary_key=True)
    rate_value = Column(Integer, nullable=False, default=1)  # 1-5 stars

    __mapper_args__ = {
        "polymorphic_identity": "rate",
    }

    __table_args__ = (
        UniqueConstraint("agent_id", "good_id", "dispute_id", name="unique_rate_per_agent_good"),
    )

    def calculate_utility(self, good_estimated_value: float, rating_weight: float) -> float:
        """Calculate utility using rating formula."""
        return math.pow(rating_weight, self.rate_value - 3) * good_estimated_value
