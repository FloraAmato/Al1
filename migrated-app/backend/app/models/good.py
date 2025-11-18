"""
Good model.
"""
import uuid
from sqlalchemy import Column, String, Numeric, Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from app.db.session import Base


class Good(Base):
    """Good model - items to be divided."""

    __tablename__ = "goods"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    dispute_id = Column(UUID(as_uuid=True), ForeignKey("disputes.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String, nullable=False)
    estimated_value = Column(Numeric(precision=19, scale=4), nullable=False)
    indivisible = Column(Boolean, default=False, nullable=False)

    # Relationships
    dispute = relationship("Dispute", back_populates="goods")
    agent_utilities = relationship("AgentUtility", back_populates="good", cascade="all, delete-orphan")
    restricted_assignments = relationship("RestrictedAssignment", back_populates="good", cascade="all, delete-orphan")

    # Constraints
    __table_args__ = (
        UniqueConstraint("name", "dispute_id", name="unique_good_name_per_dispute"),
    )
