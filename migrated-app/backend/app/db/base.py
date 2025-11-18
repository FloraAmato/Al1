"""
Import all models here for Alembic to detect them.
"""
from app.db.session import Base
from app.models.user import User, Role, user_roles
from app.models.dispute import Dispute
from app.models.agent import Agent
from app.models.good import Good
from app.models.agent_utility import AgentUtility, Bid, Rate
from app.models.restricted_assignment import RestrictedAssignment
from app.models.conversation import Conversation

__all__ = [
    "Base",
    "User",
    "Role",
    "user_roles",
    "Dispute",
    "Agent",
    "Good",
    "AgentUtility",
    "Bid",
    "Rate",
    "RestrictedAssignment",
    "Conversation",
]
