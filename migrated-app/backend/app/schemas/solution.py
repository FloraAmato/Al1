"""Solution schemas."""
from typing import List, Dict, Optional
from decimal import Decimal
from pydantic import BaseModel, UUID4, ConfigDict


class AllocationItem(BaseModel):
    """Individual allocation item."""
    agent_id: UUID4
    agent_name: str
    good_id: UUID4
    good_name: str
    allocation: float  # 0.0 to 1.0 (percentage of good allocated)


class Solution(BaseModel):
    """Optimization solution."""
    dispute_id: UUID4
    allocations: List[AllocationItem]
    agent_utilities: Dict[UUID4, Decimal]  # Total utility per agent
    total_utility: Decimal
    is_feasible: bool
    solver_status: str
    computation_time: float  # seconds


class SolutionExplanation(BaseModel):
    """LLM-generated explanation of solution."""
    solution: Solution
    explanation: str  # Natural language explanation
    fairness_metrics: Dict[str, float]
