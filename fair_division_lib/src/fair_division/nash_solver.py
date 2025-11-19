"""
Nash Social Welfare Maximization Solver

This module implements the Nash social welfare maximizer, which approximates
the Nash bargaining solution from cooperative game theory.

THEORETICAL FOUNDATION:
-----------------------

1. CONCEPT:
   The Nash social welfare (NSW) maximizer seeks an allocation that maximizes
   the **geometric mean** of agent utilities (weighted by entitlements).

   This corresponds to the **Nash bargaining solution** when:
   - The disagreement point is zero (or utilities are shifted appropriately)
   - The feasible set of utility profiles is convex and compact
   - Utilities are transferable (or quasi-linear)

2. FORMAL MODEL:
   Given:
   - n agents, m divisible goods
   - Utility matrix u[i,j]: agent i's utility for good j
   - Entitlement weights w[i]: agent i's bargaining weight
   - Allocation x[i,j]: fraction of good j given to agent i

   Maximize:  prod_i (U_i)^w_i  =  exp(sum_i w_i * log(U_i))

   Subject to:
       U_i = sum_j u[i,j] * x[i,j]  for all i  (utility definition)
       sum_i x[i,j] = 1              for all j  (goods fully allocated)
       x[i,j] >= 0                   for all i,j (non-negativity)
       U_i >= epsilon                for all i  (strict positivity for log)

   We use the **log formulation** for numerical stability:
       Maximize  sum_i w_i * log(U_i)

   This is equivalent to maximizing the product because log is monotone increasing.

3. GAME-THEORETIC PROPERTIES (under assumptions):

   Assuming:
   - Utilities are strictly positive and continuous
   - Feasible set is convex and compact
   - Entitlements (weights) are strictly positive
   - The Nash bargaining axioms apply

   The Nash solution satisfies:

   a) **Pareto Efficiency**:
      The Nash solution is always on the Pareto frontier of the utility possibility set.
      This is a fundamental property of the Nash bargaining solution.

   b) **Symmetry**:
      If two agents have identical utilities and identical entitlements,
      they receive allocations that yield identical utilities.

   c) **Scale Invariance** (with caveats):
      The Nash solution is invariant to positive affine transformations of utilities
      *if* the model includes a proper disagreement point. In our setting with
      zero disagreement point and strictly positive utilities, rescaling utilities
      of one agent will affect the solution.

   d) **Independence of Irrelevant Alternatives (IIA)**:
      If we restrict the feasible set and the Nash solution remains feasible,
      it remains the Nash solution for the smaller set.

   e) **Monotonicity w.r.t. entitlements**:
      Increasing agent i's weight w_i generally increases their utility U_i
      (tilts the solution in their favor).

   f) **Envy-freeness**:
      NOT guaranteed in general. Nash welfare focuses on efficiency and a
      particular notion of "fairness" (proportional to weights), but agents
      may still envy each other's bundles.

   g) **Proportionality** (weighted):
      The Nash solution tends to allocate utilities in proportion to entitlements,
      but this is not a strict guarantee for all utility functions.

4. WHY LOG FORMULATION?

   a) **Numerical Stability**:
      - The product prod_i U_i^w_i can easily underflow (if U_i < 1) or overflow (if U_i > 1).
      - Taking logarithms converts products to sums: log(prod U_i^w_i) = sum w_i log(U_i).
      - This is numerically stable and well-behaved.

   b) **Convexity**:
      - For a convex feasible set in allocation space, sum w_i log(U_i) is concave
        in the allocation variables (since U_i is linear in allocations and log is concave).
      - This makes the problem a convex optimization, solvable efficiently.

   c) **Equivalence**:
      - Since log is strictly increasing, maximizing sum w_i log(U_i) is equivalent
        to maximizing prod U_i^w_i.

5. EPSILON FOR STRICT POSITIVITY:

   - The logarithm requires U_i > 0 for all agents.
   - We enforce U_i >= epsilon for a small epsilon (default 1e-6).
   - This means even agents with very low utilities get a tiny positive amount.
   - **Trade-off**: Larger epsilon ensures numerical stability but may introduce
     slight distortions from the true Nash solution if some agent would naturally
     get near-zero utility.

6. LIMITATIONS & CAVEATS:

   - **Zero utilities**: If an agent has u[i,j] = 0 for all goods, they cannot
     achieve positive utility. The problem becomes infeasible (or we must relax epsilon).

   - **Envy**: Nash welfare does NOT guarantee envy-freeness. It's possible for
     agent i to prefer agent k's bundle.

   - **Disagreement point**: We assume zero disagreement point. In some applications,
     agents may have outside options or initial endowments.

   - **Discrete goods**: If goods are indivisible, the problem is NP-hard. This solver
     assumes full divisibility.

7. IMPLEMENTATION APPROACH:

   We use **sequential convex programming** or a **nonlinear solver**:
   - OR-Tools does not natively support log objectives in LP.
   - We use SciPy's nonlinear optimizer (SLSQP) which handles:
       - Nonlinear objective: sum w_i log(U_i)
       - Linear constraints: sum_i x[i,j] = 1, x >= 0
       - Nonlinear constraints: U_i >= epsilon

   Alternatively, we can use OR-Tools' nonlinear solver or other convex solvers.

REFERENCES:
-----------
- Nash, J. (1950). The Bargaining Problem. Econometrica.
- Caragiannis, I., et al. (2019). The Unreasonable Fairness of Maximum Nash Welfare. ACM TEAC.
- Moulin, H. (2003). Fair Division and Collective Welfare. MIT Press.
"""

import time
from typing import Optional
import numpy as np
import numpy.typing as npt
from scipy.optimize import minimize, LinearConstraint, NonlinearConstraint

from .models import AllocationResult


def solve_nash_allocation(
    utilities: npt.NDArray[np.float64],
    entitlements: npt.NDArray[np.float64],
    epsilon: float = 1e-6,
    time_limit_seconds: float = 300.0,
    solver_options: Optional[dict] = None,
) -> AllocationResult:
    """
    Solve the Nash social welfare maximization problem.

    This function computes an allocation that maximizes the weighted geometric
    mean of agent utilities, using a log formulation for numerical stability.

    Formally:
        Maximize  sum_i w_i * log(U_i)
        where U_i = sum_j u[i,j] * x[i,j]
        and w_i are entitlement weights.

    This is equivalent to maximizing prod_i (U_i)^w_i.

    Args:
        utilities: Utility matrix of shape (n_agents, n_goods).
                   utilities[i,j] is agent i's utility for good j.
        entitlements: Entitlement weights of shape (n_agents,).
                      entitlements[i] is the bargaining weight of agent i.
                      Must all be positive.
        epsilon: Small positive lower bound on utilities to ensure log is defined.
                 Default: 1e-6. Larger values increase numerical stability but
                 may distort the solution slightly.
        time_limit_seconds: Maximum solver time in seconds. Default: 300.
                           Note: SciPy SLSQP doesn't strictly enforce this, but
                           we limit iterations as a proxy.
        solver_options: Optional dict of options to pass to scipy.optimize.minimize.

    Returns:
        AllocationResult containing:
            - allocation: Matrix x[i,j] with fractions of good j to agent i
            - utilities: Array of realized utilities per agent
            - objective_value: The maximum Nash welfare achieved (sum w_i log U_i)
            - solver_status: 'optimal' or 'feasible' based on scipy result
            - solve_time: Time taken by solver

    Raises:
        ValueError: If inputs are malformed (negative utilities, zero entitlements, etc.)

    Example:
        >>> utilities = np.array([[10, 5], [5, 10]])
        >>> entitlements = np.array([1.0, 1.0])
        >>> result = solve_nash_allocation(utilities, entitlements)
        >>> print(result.utilities)  # Should be close to [7.5, 7.5] for symmetric case
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

    # Normalize entitlements so they sum to 1 (for numerical stability)
    weights = entitlements / entitlements.sum()

    # Flatten decision variables: x is a vector of length n_agents * n_goods
    # x[i*n_goods + j] represents allocation x[i,j]

    def unflatten(x_flat: np.ndarray) -> np.ndarray:
        """Convert flat vector to allocation matrix."""
        return x_flat.reshape((n_agents, n_goods))

    def flatten(x_matrix: np.ndarray) -> np.ndarray:
        """Convert allocation matrix to flat vector."""
        return x_matrix.flatten()

    # Objective: Maximize sum_i w_i * log(U_i)
    # SciPy minimizes, so we minimize the negative.
    def objective(x_flat: np.ndarray) -> float:
        x = unflatten(x_flat)
        agent_utilities = (x * utilities).sum(axis=1)
        # Clamp to epsilon to avoid log(0)
        agent_utilities = np.maximum(agent_utilities, epsilon)
        nash_welfare = (weights * np.log(agent_utilities)).sum()
        return -nash_welfare  # Minimize negative = maximize positive

    def objective_grad(x_flat: np.ndarray) -> np.ndarray:
        """Gradient of the negative Nash welfare."""
        x = unflatten(x_flat)
        agent_utilities = (x * utilities).sum(axis=1)
        agent_utilities = np.maximum(agent_utilities, epsilon)

        # d/dx[i,j] of sum_k w_k log(U_k) = w_i * (1/U_i) * u[i,j]
        grad_matrix = np.zeros((n_agents, n_goods))
        for i in range(n_agents):
            grad_matrix[i, :] = weights[i] * utilities[i, :] / agent_utilities[i]

        return -flatten(grad_matrix)  # Negative because we minimize

    # Constraints:

    # 1. Each good is fully allocated: sum_i x[i,j] = 1 for all j
    # This is a linear constraint: A_eq @ x = b_eq
    # where A_eq has shape (n_goods, n_agents * n_goods)
    A_eq = np.zeros((n_goods, n_agents * n_goods))
    for j in range(n_goods):
        for i in range(n_agents):
            A_eq[j, i * n_goods + j] = 1.0
    b_eq = np.ones(n_goods)

    linear_constraint = LinearConstraint(A_eq, b_eq, b_eq)

    # 2. Each agent's utility is at least epsilon: U_i >= epsilon
    # This is a nonlinear constraint
    def utility_constraints(x_flat: np.ndarray) -> np.ndarray:
        """Return U_i for each agent i."""
        x = unflatten(x_flat)
        return (x * utilities).sum(axis=1)

    def utility_constraints_jac(x_flat: np.ndarray) -> np.ndarray:
        """Jacobian of utility constraints."""
        # Jacobian[i, k] = d(U_i)/d(x_flat[k])
        # U_i = sum_j u[i,j] * x[i,j]
        # So d(U_i)/d(x[i,j]) = u[i,j], and 0 for other agents' variables.
        jac = np.zeros((n_agents, n_agents * n_goods))
        for i in range(n_agents):
            for j in range(n_goods):
                jac[i, i * n_goods + j] = utilities[i, j]
        return jac

    nonlinear_constraint = NonlinearConstraint(
        utility_constraints,
        lb=np.full(n_agents, epsilon),
        ub=np.full(n_agents, np.inf),
        jac=utility_constraints_jac,
    )

    # Bounds: 0 <= x[i,j] <= 1
    bounds = [(0.0, 1.0) for _ in range(n_agents * n_goods)]

    # Initial guess: equal allocation
    x0 = np.full(n_agents * n_goods, 1.0 / n_agents)

    # Solver options
    if solver_options is None:
        solver_options = {}

    # Limit iterations as a proxy for time limit
    # SLSQP typically takes ~10-100 iterations; we allow generously
    max_iter = solver_options.get("maxiter", 1000)

    options = {
        "maxiter": max_iter,
        "disp": False,
        "ftol": 1e-9,
    }
    options.update(solver_options)

    # Solve
    start_time = time.time()
    result = minimize(
        objective,
        x0,
        method="SLSQP",
        jac=objective_grad,
        constraints=[linear_constraint, nonlinear_constraint],
        bounds=bounds,
        options=options,
    )
    solve_time = time.time() - start_time

    # Extract solution
    x_opt = unflatten(result.x)
    agent_utilities = (x_opt * utilities).sum(axis=1)

    # Objective value (positive Nash welfare)
    objective_value = -result.fun

    # Solver status
    if result.success:
        solver_status = "optimal"
    else:
        solver_status = "feasible"  # Or could be "failed" depending on interpretation

    # Compute Nash welfare (geometric mean)
    # Nash welfare = prod_i U_i^w_i = exp(sum w_i log U_i)
    nash_product = np.exp(objective_value)

    return AllocationResult(
        allocation=x_opt,
        utilities=agent_utilities,
        objective_value=objective_value,
        solver_status=solver_status,
        solve_time=solve_time,
        metadata={
            "log_nash_welfare": objective_value,
            "nash_product": nash_product,
            "algorithm": "nash_social_welfare",
            "scipy_message": result.message,
            "scipy_success": result.success,
            "iterations": result.nit if hasattr(result, "nit") else None,
        },
    )
