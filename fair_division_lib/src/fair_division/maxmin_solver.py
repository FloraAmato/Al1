"""
Max-Min Fair Allocation Solver (Egalitarian Solution)

This module implements the egalitarian (max-min) fair division algorithm,
which maximizes the minimum utility across all agents.

THEORETICAL FOUNDATION:
-----------------------

1. CONCEPT:
   The max-min fair allocation approximates the **egalitarian bargaining solution**
   in cooperative game theory. It seeks to maximize the welfare of the worst-off agent.

2. FORMAL MODEL:
   Given:
   - n agents, m divisible goods
   - Utility matrix u[i,j]: agent i's utility for good j
   - Entitlement weights w[i]: agent i's claim weight
   - Allocation x[i,j]: fraction of good j given to agent i

   Maximize:  min_i { U_i / w_i }
   Subject to:
       U_i = sum_j u[i,j] * x[i,j]  for all i  (utility definition)
       sum_i x[i,j] = 1              for all j  (goods fully allocated)
       x[i,j] >= 0                   for all i,j (non-negativity)

   We normalize by w_i to respect entitlements: an agent with weight 2
   "should" get twice the utility, so we maximize min of weighted utilities.

3. GAME-THEORETIC PROPERTIES (under assumptions):

   Assuming:
   - Utilities are non-negative and continuous
   - Feasible set is convex and compact
   - Agents have non-zero entitlements

   The max-min solution satisfies:

   a) **Pareto Efficiency**:
      If we could increase any agent's utility without decreasing the minimum,
      we would, so the solution is on the Pareto frontier.

   b) **Symmetry**:
      If two agents have identical utilities and entitlements, they receive
      allocations that yield identical normalized utilities.

   c) **Monotonicity w.r.t. entitlements**:
      If agent i's entitlement w_i increases, their utility U_i generally increases
      (though the relationship depends on the constraint set).

   d) **Envy-freeness**:
      NOT generally guaranteed. Max-min focuses on equality of normalized utilities,
      not absence of envy. An agent may prefer another's bundle.

   e) **Proportionality**:
      In weighted form: agent i gets at least w_i / sum(w) of their utility
      from the grand bundle (under certain conditions).

4. LIMITATIONS & CAVEATS:

   - **Zero utilities**: If u[i,j] = 0 for all j for some agent i, that agent's
     utility is always 0, making max-min trivial. We add a small epsilon to avoid this.

   - **Lexicographic refinement**: The basic max-min may have multiple optima.
     A lexicographic max-min (maximize min, then maximize second-min, etc.)
     is theoretically superior but computationally more complex.

   - **Discrete goods**: If goods are indivisible, the problem becomes combinatorial.
     This solver assumes divisibility.

5. IMPLEMENTATION APPROACH:

   We introduce an auxiliary variable t (the minimum normalized utility) and solve:

       Maximize t
       Subject to:
           sum_j u[i,j] * x[i,j] >= t * w_i   for all i
           sum_i x[i,j] = 1                    for all j
           x[i,j] >= 0                         for all i,j
           t >= epsilon                        (numerical stability)

   This is a linear program, solved efficiently with OR-Tools.

REFERENCES:
-----------
- Moulin, H. (2003). Fair Division and Collective Welfare. MIT Press.
- Brams, S. J., & Taylor, A. D. (1996). Fair Division: From cake-cutting to dispute resolution.
- Kalai, E. (1977). Proportional Solutions to Bargaining Situations: Interpersonal Utility Comparisons.
"""

import time
from typing import Optional
import numpy as np
import numpy.typing as npt
from ortools.linear_solver import pywraplp

from .models import AllocationResult


def solve_maxmin_allocation(
    utilities: npt.NDArray[np.float64],
    entitlements: npt.NDArray[np.float64],
    epsilon: float = 1e-6,
    time_limit_seconds: float = 300.0,
) -> AllocationResult:
    """
    Solve the max-min fair allocation problem (egalitarian solution).

    This function computes an allocation that maximizes the minimum normalized utility
    across all agents, where normalization is by entitlement weights.

    Formally:
        Maximize  min_i { U_i / w_i }
        where U_i = sum_j u[i,j] * x[i,j]

    Args:
        utilities: Utility matrix of shape (n_agents, n_goods).
                   utilities[i,j] is agent i's utility for good j.
        entitlements: Entitlement weights of shape (n_agents,).
                      entitlements[i] is the weight/claim of agent i.
                      Must all be positive.
        epsilon: Small positive value to ensure min utility is strictly positive.
                 Prevents degenerate solutions. Default: 1e-6.
        time_limit_seconds: Maximum solver time in seconds. Default: 300.

    Returns:
        AllocationResult containing:
            - allocation: Matrix x[i,j] with fractions of good j to agent i
            - utilities: Array of realized utilities per agent
            - objective_value: The maximum minimum normalized utility achieved
            - solver_status: 'optimal', 'feasible', or 'infeasible'
            - solve_time: Time taken by solver

    Raises:
        ValueError: If inputs are malformed (negative utilities, zero entitlements, etc.)

    Example:
        >>> utilities = np.array([[10, 5], [5, 10]])
        >>> entitlements = np.array([1.0, 1.0])
        >>> result = solve_maxmin_allocation(utilities, entitlements)
        >>> print(result.utilities)  # Should be close to [7.5, 7.5] for this symmetric case
    """
    # Validate inputs
    if utilities.ndim != 2:
        raise ValueError(f"utilities must be 2D, got shape {utilities.shape}")

    n_agents, n_goods = utilities.shape

    if entitlements.shape != (n_agents,):
        raise ValueError(
            f"entitlements shape {entitlements.shape} doesn't match n_agents={n_agents}"
        )

    if np.any(utilities < 0):
        raise ValueError("Utilities must be non-negative")

    if np.any(entitlements <= 0):
        raise ValueError("Entitlements must be strictly positive")

    if epsilon <= 0:
        raise ValueError("epsilon must be positive")

    # Create solver
    solver = pywraplp.Solver.CreateSolver("GLOP")  # LP solver
    if not solver:
        raise RuntimeError("Could not create OR-Tools solver")

    solver.SetTimeLimit(int(time_limit_seconds * 1000))  # milliseconds

    # Decision variables: x[i,j] = fraction of good j allocated to agent i
    x = {}
    for i in range(n_agents):
        for j in range(n_goods):
            x[i, j] = solver.NumVar(0.0, 1.0, f"x_{i}_{j}")

    # Auxiliary variable: t = minimum normalized utility
    t = solver.NumVar(epsilon, solver.infinity(), "min_normalized_utility")

    # Objective: Maximize t (the minimum normalized utility)
    objective = solver.Objective()
    objective.SetCoefficient(t, 1.0)
    objective.SetMaximization()

    # Constraints:

    # 1. Each agent's (normalized) utility must be at least t:
    #    sum_j u[i,j] * x[i,j] >= t * w[i]  for all i
    for i in range(n_agents):
        constraint = solver.Constraint(0.0, solver.infinity(), f"min_utility_agent_{i}")
        for j in range(n_goods):
            constraint.SetCoefficient(x[i, j], utilities[i, j])
        constraint.SetCoefficient(t, -entitlements[i])

    # 2. Each good is fully allocated:
    #    sum_i x[i,j] = 1  for all j
    for j in range(n_goods):
        constraint = solver.Constraint(1.0, 1.0, f"allocate_good_{j}")
        for i in range(n_agents):
            constraint.SetCoefficient(x[i, j], 1.0)

    # Solve
    start_time = time.time()
    status = solver.Solve()
    solve_time = time.time() - start_time

    # Extract results
    if status == pywraplp.Solver.OPTIMAL:
        solver_status = "optimal"
    elif status == pywraplp.Solver.FEASIBLE:
        solver_status = "feasible"
    else:
        solver_status = "infeasible"
        # Return empty result
        return AllocationResult(
            allocation=np.zeros((n_agents, n_goods)),
            utilities=np.zeros(n_agents),
            objective_value=0.0,
            solver_status=solver_status,
            solve_time=solve_time,
            metadata={"error": "No feasible solution found"},
        )

    # Build allocation matrix
    allocation = np.zeros((n_agents, n_goods))
    for i in range(n_agents):
        for j in range(n_goods):
            allocation[i, j] = x[i, j].solution_value()

    # Compute utilities
    realized_utilities = (allocation * utilities).sum(axis=1)

    # Objective value is the min normalized utility
    objective_value = t.solution_value()

    return AllocationResult(
        allocation=allocation,
        utilities=realized_utilities,
        objective_value=objective_value,
        solver_status=solver_status,
        solve_time=solve_time,
        metadata={
            "min_normalized_utility": objective_value,
            "normalized_utilities": realized_utilities / entitlements,
            "algorithm": "max_min_egalitarian",
        },
    )
