"""
Max-Min Fairness allocation algorithm.

Maximizes the minimum agent utility subject to entitlement constraints.
"""
from typing import Dict, List, Tuple
import numpy as np
from scipy.optimize import linprog

from app.core.logging import get_logger

logger = get_logger(__name__)


class MaxMinSolver:
    """
    Solver for max-min fairness allocation.

    Formulation:
    maximize   t
    subject to:
        - For each agent i: sum_j(x_ij * u_ij) >= t  (utility >= min)
        - For each good j: sum_i(x_ij) <= 1  (goods fully allocated)
        - Budget constraint: sum_ij(x_ij * v_j) <= B
        - x_ij >= 0
        - Restricted assignments enforced
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
        self.n_vars = self.n_agents * self.n_goods + 1  # x_ij + t

        logger.info(
            f"MaxMin solver initialized: {self.n_agents} agents, "
            f"{self.n_goods} goods, budget={budget}"
        )

    def solve(self) -> Tuple[Dict[Tuple[int, int], float], float]:
        """
        Solve the max-min allocation problem.

        Returns:
            Tuple of (allocations, objective_value)
            allocations: Dict mapping (agent_id, good_id) -> amount
            objective_value: The maximized minimum utility
        """
        logger.info("Solving max-min fairness problem...")

        # Build linear program
        # Variables: [x_00, x_01, ..., x_ij, ..., t]
        # Objective: maximize t => minimize -t

        # Objective coefficients
        c = np.zeros(self.n_vars)
        c[-1] = -1.0  # Minimize -t (i.e., maximize t)

        # Inequality constraints (A_ub @ x <= b_ub)
        A_ub = []
        b_ub = []

        # 1. For each agent: -sum_j(x_ij * u_ij) + t <= 0
        #    (equivalent to: sum_j(x_ij * u_ij) >= t)
        for i, agent_id in enumerate(self.agents):
            row = np.zeros(self.n_vars)
            for j, good_id in enumerate(self.goods):
                idx = i * self.n_goods + j
                utility = self.utilities.get((agent_id, good_id), 0.0)
                row[idx] = -utility
            row[-1] = 1.0  # t coefficient
            A_ub.append(row)
            b_ub.append(0.0)

        # 2. For each good: sum_i(x_ij) <= 1
        for j, good_id in enumerate(self.goods):
            row = np.zeros(self.n_vars)
            for i in range(self.n_agents):
                idx = i * self.n_goods + j
                row[idx] = 1.0
            A_ub.append(row)
            b_ub.append(1.0)

        # 3. Budget constraint: sum_ij(x_ij * v_j) <= budget
        row = np.zeros(self.n_vars)
        for i in range(self.n_agents):
            for j, good_id in enumerate(self.goods):
                idx = i * self.n_goods + j
                value = self.good_values.get(good_id, 0.0)
                row[idx] = value
        A_ub.append(row)
        b_ub.append(self.budget)

        A_ub = np.array(A_ub)
        b_ub = np.array(b_ub)

        # Bounds: x_ij >= 0, t >= 0
        bounds = [(0, None)] * self.n_vars

        # Handle restrictions
        for (agent_id, good_id), allowed in self.restrictions.items():
            if not allowed:
                i = self.agents.index(agent_id)
                j = self.goods.index(good_id)
                idx = i * self.n_goods + j
                bounds[idx] = (0, 0)  # Force to 0

        # Solve
        try:
            result = linprog(
                c,
                A_ub=A_ub,
                b_ub=b_ub,
                bounds=bounds,
                method='highs',
            )

            if not result.success:
                logger.error(f"Optimization failed: {result.message}")
                raise ValueError(f"Optimization failed: {result.message}")

            # Extract allocations
            allocations = {}
            for i, agent_id in enumerate(self.agents):
                for j, good_id in enumerate(self.goods):
                    idx = i * self.n_goods + j
                    amount = result.x[idx]
                    if amount > 1e-6:  # Filter out near-zero values
                        allocations[(agent_id, good_id)] = amount

            objective_value = result.x[-1]  # The 't' variable

            logger.info(f"Max-min solution found: min_utility={objective_value:.4f}")
            return allocations, objective_value

        except Exception as e:
            logger.error(f"Solver error: {e}")
            raise
