"""
Restricted assignment model.
"""
import uuid
from sqlalchemy import Column, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from app.db.session import Base


class RestrictedAssignment(Base):
    """Restricted assignment model - constraints on agent-good assignments."""

    __tablename__ = "restricted_assignments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    agent_id = Column(UUID(as_uuid=True), ForeignKey("agents.id", ondelete="CASCADE"), nullable=False, index=True)
    good_id = Column(UUID(as_uuid=True), ForeignKey("goods.id", ondelete="CASCADE"), nullable=False, index=True)
    dispute_id = Column(UUID(as_uuid=True), ForeignKey("disputes.id", ondelete="CASCADE"), nullable=False, index=True)

    # Share of entitlement for this specific assignment (0.0 to 1.0)
    share_of_entitlement = Column(Numeric(precision=3, scale=2), nullable=False, default=0)

    # Relationships
    agent = relationship("Agent", back_populates="restricted_assignments")
    good = relationship("Good", back_populates="restricted_assignments")
    dispute = relationship("Dispute", back_populates="restricted_assignments")
