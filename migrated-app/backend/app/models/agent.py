"""
Agent model.
"""
import enum
import uuid
from sqlalchemy import Column, String, Float, Integer, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import UniqueConstraint
from app.db.session import Base


class ValidatedSteps(str, enum.Enum):
    """Agent validation status."""
    NONE = "none"
    SETUP = "setup"
    BIDS = "bids"
    AGREEMENT = "agreement"
    DISAGREEMENT = "disagreement"


class Agent(Base):
    """Agent model - participants in a dispute."""

    __tablename__ = "agents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True)
    dispute_id = Column(UUID(as_uuid=True), ForeignKey("disputes.id", ondelete="CASCADE"), nullable=False, index=True)
    email = Column(String, nullable=False, index=True)

    # Share of entitlement (0.0 to 1.0)
    share_of_entitlement = Column(Float, default=0.0, nullable=False)

    # Validation status
    validated = Column(Enum(ValidatedSteps), default=ValidatedSteps.NONE, nullable=False)

    # Relationships
    user = relationship("User", back_populates="agents")
    dispute = relationship("Dispute", back_populates="agents")
    agent_utilities = relationship("AgentUtility", back_populates="agent", cascade="all, delete-orphan")
    restricted_assignments = relationship("RestrictedAssignment", back_populates="agent", cascade="all, delete-orphan")

    # Constraints
    __table_args__ = (
        UniqueConstraint("email", "dispute_id", name="unique_agent_email_per_dispute"),
    )

    @property
    def name(self) -> str:
        """Get agent name from linked user or email."""
        if self.user:
            return self.user.full_name
        return self.email
