"""
Nash Social Welfare allocation algorithm.

Maximizes the product of agent utilities weighted by entitlements.
"""
from typing import Dict, List, Tuple
import numpy as np
from scipy.optimize import minimize

from app.core.logging import get_logger

logger = get_logger(__name__)


class NashSolver:
    """
    Solver for Nash social welfare allocation.

    Formulation:
    maximize   product_i(U_i ^ w_i)
    subject to:
        - For each good j: sum_i(x_ij) <= 1
        - Budget constraint: sum_ij(x_ij * v_j) <= B
        - x_ij >= 0
        - Restricted assignments enforced

    Where:
        - U_i = sum_j(x_ij * u_ij) is agent i's total utility
        - w_i is agent i's entitlement weight
    """

    def __init__(
        self,
        agents: List[int],
        goods: List[int],
        utilities: Dict[Tuple[int, int], float],
        entitlements: Dict[int, float],
        good_values: Dict[int, float],
        budget: float,
        restrictions: Dict[Tuple[int, int], bool] = None,
    ):
        """
        Initialize the solver.

        Args:
            agents: List of agent IDs
            goods: List of good IDs
            utilities: Dict mapping (agent_id, good_id) -> utility
            entitlements: Dict mapping agent_id -> entitlement share
            good_values: Dict mapping good_id -> estimated value
            budget: Total budget for allocation
            restrictions: Dict mapping (agent_id, good_id) -> allowed (True/False)
        """
        self.agents = agents
        self.goods = goods
        self.utilities = utilities
        self.entitlements = entitlements
        self.good_values = good_values
        self.budget = budget
        self.restrictions = restrictions or {}

        self.n_agents = len(agents)
        self.n_goods = len(goods)
        self.n_vars = self.n_agents * self.n_goods

        logger.info(
            f"Nash solver initialized: {self.n_agents} agents, "
            f"{self.n_goods} goods, budget={budget}"
        )

    def _objective(self, x: np.ndarray) -> float:
        """
        Objective function: negative log of Nash social welfare.

        We minimize -sum_i(w_i * log(U_i + epsilon))
        (equivalent to maximizing product_i(U_i ^ w_i))
        """
        epsilon = 1e-8  # Small constant to avoid log(0)

        log_sum = 0.0
        for i, agent_id in enumerate(self.agents):
            utility = 0.0
            for j, good_id in enumerate(self.goods):
                idx = i * self.n_goods + j
                u_ij = self.utilities.get((agent_id, good_id), 0.0)
                utility += x[idx] * u_ij

            weight = self.entitlements.get(agent_id, 1.0 / self.n_agents)
            log_sum += weight * np.log(utility + epsilon)

        return -log_sum  # Negative because we minimize

    def _constraint_goods(self, x: np.ndarray, j: int) -> float:
        """Constraint: sum_i(x_ij) <= 1 for each good j."""
        total = 0.0
        for i in range(self.n_agents):
            idx = i * self.n_goods + j
            total += x[idx]
        return 1.0 - total  # >= 0 means constraint satisfied

    def _constraint_budget(self, x: np.ndarray) -> float:
        """Constraint: sum_ij(x_ij * v_j) <= budget."""
        total_cost = 0.0
        for i in range(self.n_agents):
            for j, good_id in enumerate(self.goods):
                idx = i * self.n_goods + j
                value = self.good_values.get(good_id, 0.0)
                total_cost += x[idx] * value
        return self.budget - total_cost  # >= 0 means constraint satisfied

    def solve(self) -> Tuple[Dict[Tuple[int, int], float], float]:
        """
        Solve the Nash social welfare allocation problem.

        Returns:
            Tuple of (allocations, objective_value)
            allocations: Dict mapping (agent_id, good_id) -> amount
            objective_value: The Nash social welfare value
        """
        logger.info("Solving Nash social welfare problem...")

        # Initial guess: equal split
        x0 = np.ones(self.n_vars) / self.n_agents

        # Bounds: x_ij >= 0
        bounds = [(0, None)] * self.n_vars

        # Handle restrictions
        for (agent_id, good_id), allowed in self.restrictions.items():
            if not allowed:
                i = self.agents.index(agent_id)
                j = self.goods.index(good_id)
                idx = i * self.n_goods + j
                bounds[idx] = (0, 0)

        # Constraints
        constraints = []

        # Good allocation constraints
        for j in range(self.n_goods):
            constraints.append({
                'type': 'ineq',
                'fun': lambda x, j=j: self._constraint_goods(x, j)
            })

        # Budget constraint
        constraints.append({
            'type': 'ineq',
            'fun': self._constraint_budget
        })

        # Solve
        try:
            result = minimize(
                self._objective,
                x0,
                method='SLSQP',
                bounds=bounds,
                constraints=constraints,
                options={'maxiter': 1000}
            )

            if not result.success:
                logger.warning(f"Optimization warning: {result.message}")

            # Extract allocations
            allocations = {}
            for i, agent_id in enumerate(self.agents):
                for j, good_id in enumerate(self.goods):
                    idx = i * self.n_goods + j
                    amount = result.x[idx]
                    if amount > 1e-6:
                        allocations[(agent_id, good_id)] = amount

            # Compute Nash social welfare value
            nash_value = np.exp(-result.fun)

            logger.info(f"Nash solution found: welfare={nash_value:.4f}")
            return allocations, nash_value

        except Exception as e:
            logger.error(f"Solver error: {e}")
            raise
