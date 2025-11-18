"""
Optimization service using OR-Tools for fair division.
"""
import time
from typing import List, Dict, Tuple
from decimal import Decimal
import math
from ortools.linear_solver import pywraplp
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.dispute import Dispute, DisputeResolutionMethod
from app.models.agent import Agent
from app.models.good import Good
from app.models.agent_utility import AgentUtility, Bid, Rate
from app.models.restricted_assignment import RestrictedAssignment
from app.schemas.solution import Solution, AllocationItem


class OptimizationService:
    """Service for solving fair division problems using OR-Tools."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def solve_dispute(self, dispute_id: str) -> Solution:
        """
        Solve a dispute using the appropriate resolution method.

        Args:
            dispute_id: UUID of the dispute to solve

        Returns:
            Solution object with allocations and utilities
        """
        # Load dispute with all related data
        result = await self.db.execute(
            select(Dispute)
            .options(
                selectinload(Dispute.agents).selectinload(Agent.user),
                selectinload(Dispute.goods),
                selectinload(Dispute.agent_utilities),
                selectinload(Dispute.restricted_assignments),
            )
            .where(Dispute.id == dispute_id)
        )
        dispute = result.scalar_one_or_none()

        if not dispute:
            raise ValueError(f"Dispute {dispute_id} not found")

        start_time = time.time()

        if dispute.resolution_method == DisputeResolutionMethod.BIDS:
            solution = self._solve_bids(dispute)
        else:
            solution = self._solve_ratings(dispute)

        computation_time = time.time() - start_time
        solution.computation_time = computation_time

        return solution

    def _solve_bids(self, dispute: Dispute) -> Solution:
        """Solve dispute using bid-based method."""
        # Create solver
        solver = pywraplp.Solver.CreateSolver("GLOP")
        if not solver:
            raise RuntimeError("Could not create solver")

        agents = list(dispute.agents)
        goods = list(dispute.goods)
        num_agents = len(agents)
        num_goods = len(goods)

        # Create decision variables: x[i][j] = allocation of good j to agent i
        x = {}
        for i, agent in enumerate(agents):
            for j, good in enumerate(goods):
                x[i, j] = solver.NumVar(0, 1, f"x_{i}_{j}")

        # Get bids
        bids = {}
        for bid in dispute.agent_utilities:
            if isinstance(bid, Bid):
                agent_idx = next((i for i, a in enumerate(agents) if a.id == bid.agent_id), None)
                good_idx = next((j for j, g in enumerate(goods) if g.id == bid.good_id), None)
                if agent_idx is not None and good_idx is not None:
                    bids[agent_idx, good_idx] = float(bid.bid_value)

        # Objective: Maximize total utility
        objective = solver.Objective()
        for (i, j), bid_value in bids.items():
            objective.SetCoefficient(x[i, j], bid_value)
        objective.SetMaximization()

        # Constraint 1: Each good is fully allocated (sum of allocations = 1)
        for j in range(num_goods):
            constraint = solver.Constraint(1, 1, f"good_{j}_allocated")
            for i in range(num_agents):
                constraint.SetCoefficient(x[i, j], 1)

        # Constraint 2: Indivisible goods (binary allocation)
        for j, good in enumerate(goods):
            if good.indivisible:
                for i in range(num_agents):
                    x[i, j].SetInteger(True)

        # Constraint 3: Budget constraints (agent can't exceed their entitlement)
        total_value = sum(float(g.estimated_value) for g in goods)
        for i, agent in enumerate(agents):
            share = agent.share_of_entitlement if agent.share_of_entitlement > 0 else dispute.agents_share_of_entitlement
            max_value = total_value * share * (1 + dispute.bounds_percentage)

            constraint = solver.Constraint(0, max_value, f"agent_{i}_budget")
            for j, good in enumerate(goods):
                constraint.SetCoefficient(x[i, j], float(good.estimated_value))

        # Constraint 4: Restricted assignments
        for restriction in dispute.restricted_assignments:
            agent_idx = next((i for i, a in enumerate(agents) if a.id == restriction.agent_id), None)
            good_idx = next((j for j, g in enumerate(goods) if g.id == restriction.good_id), None)
            if agent_idx is not None and good_idx is not None:
                # This agent-good pair has a maximum share restriction
                max_share = float(restriction.share_of_entitlement)
                x[agent_idx, good_idx].SetBounds(0, max_share)

        # Solve
        status = solver.Solve()

        # Extract solution
        allocations = []
        agent_utilities = {}

        for i, agent in enumerate(agents):
            total_utility = Decimal(0)
            for j, good in enumerate(goods):
                allocation_value = x[i, j].solution_value()
                if allocation_value > 0.001:  # Only include non-zero allocations
                    allocations.append(
                        AllocationItem(
                            agent_id=agent.id,
                            agent_name=agent.name,
                            good_id=good.id,
                            good_name=good.name,
                            allocation=allocation_value,
                        )
                    )
                    utility = bids.get((i, j), 0) * allocation_value
                    total_utility += Decimal(str(utility))

            agent_utilities[agent.id] = total_utility

        is_feasible = status == pywraplp.Solver.OPTIMAL
        solver_status = "OPTIMAL" if is_feasible else "INFEASIBLE"

        return Solution(
            dispute_id=dispute.id,
            allocations=allocations,
            agent_utilities=agent_utilities,
            total_utility=sum(agent_utilities.values()),
            is_feasible=is_feasible,
            solver_status=solver_status,
            computation_time=0,  # Will be set by caller
        )

    def _solve_ratings(self, dispute: Dispute) -> Solution:
        """Solve dispute using rating-based method."""
        # Similar to _solve_bids but using calculated utilities from ratings
        solver = pywraplp.Solver.CreateSolver("GLOP")
        if not solver:
            raise RuntimeError("Could not create solver")

        agents = list(dispute.agents)
        goods = list(dispute.goods)
        num_agents = len(agents)
        num_goods = len(goods)

        # Create decision variables
        x = {}
        for i in range(num_agents):
            for j in range(num_goods):
                x[i, j] = solver.NumVar(0, 1, f"x_{i}_{j}")

        # Calculate utilities from ratings
        utilities = {}
        for rate in dispute.agent_utilities:
            if isinstance(rate, Rate):
                agent_idx = next((i for i, a in enumerate(agents) if a.id == rate.agent_id), None)
                good_idx = next((j for j, g in enumerate(goods) if g.id == rate.good_id), None)
                if agent_idx is not None and good_idx is not None:
                    good_value = float(goods[good_idx].estimated_value)
                    utility = rate.calculate_utility(good_value, dispute.rating_weight)
                    utilities[agent_idx, good_idx] = utility

        # Objective: Maximize total utility
        objective = solver.Objective()
        for (i, j), utility in utilities.items():
            objective.SetCoefficient(x[i, j], utility)
        objective.SetMaximization()

        # Constraints (same as bids)
        for j in range(num_goods):
            constraint = solver.Constraint(1, 1, f"good_{j}_allocated")
            for i in range(num_agents):
                constraint.SetCoefficient(x[i, j], 1)

        for j, good in enumerate(goods):
            if good.indivisible:
                for i in range(num_agents):
                    x[i, j].SetInteger(True)

        # Solve
        status = solver.Solve()

        # Extract solution
        allocations = []
        agent_utilities = {}

        for i, agent in enumerate(agents):
            total_utility = Decimal(0)
            for j, good in enumerate(goods):
                allocation_value = x[i, j].solution_value()
                if allocation_value > 0.001:
                    allocations.append(
                        AllocationItem(
                            agent_id=agent.id,
                            agent_name=agent.name,
                            good_id=good.id,
                            good_name=good.name,
                            allocation=allocation_value,
                        )
                    )
                    utility = utilities.get((i, j), 0) * allocation_value
                    total_utility += Decimal(str(utility))

            agent_utilities[agent.id] = total_utility

        is_feasible = status == pywraplp.Solver.OPTIMAL
        solver_status = "OPTIMAL" if is_feasible else "INFEASIBLE"

        return Solution(
            dispute_id=dispute.id,
            allocations=allocations,
            agent_utilities=agent_utilities,
            total_utility=sum(agent_utilities.values()),
            is_feasible=is_feasible,
            solver_status=solver_status,
            computation_time=0,
        )
