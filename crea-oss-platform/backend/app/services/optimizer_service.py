"""
OptimizerService for running game-theory allocations.

Integrates max-min and Nash solvers with the dispute model.
"""
import time
from typing import Dict, List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.logging import get_logger
from app.models import (
    Dispute,
    Agent,
    Good,
    AgentUtility,
    RestrictedAssignment,
    Solution,
    AllocationItem,
)
from app.algorithms import MaxMinSolver, NashSolver

logger = get_logger(__name__)


class OptimizerService:
    """
    Service for computing fair allocations using game-theory algorithms.
    """

    def __init__(self, db: AsyncSession):
        """Initialize the service with a database session."""
        self.db = db

    async def run_maxmin(self, dispute_id: int) -> Solution:
        """
        Run max-min fairness allocation for a dispute.

        Args:
            dispute_id: ID of the dispute

        Returns:
            Solution object with allocations
        """
        logger.info(f"Running max-min allocation for dispute {dispute_id}")
        start_time = time.time()

        # Load dispute data
        data = await self._load_dispute_data(dispute_id)

        # Run solver
        solver = MaxMinSolver(
            agents=data["agent_ids"],
            goods=data["good_ids"],
            utilities=data["utilities"],
            entitlements=data["entitlements"],
            good_values=data["good_values"],
            budget=data["budget"],
            restrictions=data["restrictions"],
        )

        allocations, objective_value = solver.solve()

        # Store solution
        elapsed_ms = (time.time() - start_time) * 1000
        solution = await self._store_solution(
            dispute_id=dispute_id,
            method="maxmin",
            allocations=allocations,
            objective_value=objective_value,
            computation_time_ms=elapsed_ms,
        )

        logger.info(f"Max-min solution computed in {elapsed_ms:.2f}ms")
        return solution

    async def run_nash(self, dispute_id: int) -> Solution:
        """
        Run Nash social welfare allocation for a dispute.

        Args:
            dispute_id: ID of the dispute

        Returns:
            Solution object with allocations
        """
        logger.info(f"Running Nash allocation for dispute {dispute_id}")
        start_time = time.time()

        # Load dispute data
        data = await self._load_dispute_data(dispute_id)

        # Run solver
        solver = NashSolver(
            agents=data["agent_ids"],
            goods=data["good_ids"],
            utilities=data["utilities"],
            entitlements=data["entitlements"],
            good_values=data["good_values"],
            budget=data["budget"],
            restrictions=data["restrictions"],
        )

        allocations, objective_value = solver.solve()

        # Store solution
        elapsed_ms = (time.time() - start_time) * 1000
        solution = await self._store_solution(
            dispute_id=dispute_id,
            method="nash",
            allocations=allocations,
            objective_value=objective_value,
            computation_time_ms=elapsed_ms,
        )

        logger.info(f"Nash solution computed in {elapsed_ms:.2f}ms")
        return solution

    async def _load_dispute_data(self, dispute_id: int) -> Dict:
        """Load all necessary data for a dispute."""
        # Load dispute with relationships
        result = await self.db.execute(
            select(Dispute).where(Dispute.id == dispute_id)
        )
        dispute = result.scalar_one_or_none()

        if not dispute:
            raise ValueError(f"Dispute {dispute_id} not found")

        # Load agents
        agents_result = await self.db.execute(
            select(Agent).where(Agent.dispute_id == dispute_id)
        )
        agents = agents_result.scalars().all()

        # Load goods
        goods_result = await self.db.execute(
            select(Good).where(Good.dispute_id == dispute_id)
        )
        goods = goods_result.scalars().all()

        # Load agent utilities
        utilities_result = await self.db.execute(
            select(AgentUtility).where(AgentUtility.dispute_id == dispute_id)
        )
        utilities_list = utilities_result.scalars().all()

        # Load restrictions
        restrictions_result = await self.db.execute(
            select(RestrictedAssignment).where(RestrictedAssignment.dispute_id == dispute_id)
        )
        restrictions_list = restrictions_result.scalars().all()

        # Build data structures
        agent_ids = [a.id for a in agents]
        good_ids = [g.id for g in goods]

        utilities = {
            (u.agent_id, u.good_id): u.utility
            for u in utilities_list
        }

        entitlements = {
            a.id: a.share_of_entitlement if a.share_of_entitlement > 0
            else dispute.agents_share_of_entitlement
            for a in agents
        }

        good_values = {g.id: g.estimated_value for g in goods}

        restrictions = {
            (r.agent_id, r.good_id): r.allowed
            for r in restrictions_list
        }

        budget = dispute.dispute_budget

        return {
            "agent_ids": agent_ids,
            "good_ids": good_ids,
            "utilities": utilities,
            "entitlements": entitlements,
            "good_values": good_values,
            "restrictions": restrictions,
            "budget": budget,
        }

    async def _store_solution(
        self,
        dispute_id: int,
        method: str,
        allocations: Dict[Tuple[int, int], float],
        objective_value: float,
        computation_time_ms: float,
    ) -> Solution:
        """Store a solution in the database."""
        # Create solution
        solution = Solution(
            dispute_id=dispute_id,
            method=method,
            objective_value=objective_value,
            computation_time_ms=computation_time_ms,
        )
        self.db.add(solution)
        await self.db.flush()  # Get solution ID

        # Create allocation items
        for (agent_id, good_id), amount in allocations.items():
            item = AllocationItem(
                solution_id=solution.id,
                agent_id=agent_id,
                good_id=good_id,
                amount=amount,
            )
            self.db.add(item)

        await self.db.commit()
        await self.db.refresh(solution)

        return solution
