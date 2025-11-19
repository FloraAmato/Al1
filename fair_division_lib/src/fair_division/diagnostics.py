"""
Fairness Diagnostics Module

This module provides comprehensive analysis of allocations against
standard game-theoretic fairness and efficiency criteria.

FAIRNESS & EFFICIENCY CONCEPTS:
--------------------------------

1. **Pareto Efficiency**:
   An allocation is Pareto efficient if no other allocation exists that
   makes at least one agent better off without making any agent worse off.

   In practice, checking Pareto efficiency requires solving optimization
   problems or enumerating alternatives. We provide a heuristic check that
   looks for obvious inefficiencies.

2. **Envy-Freeness (EF)**:
   An allocation is envy-free if no agent i prefers another agent k's bundle
   to their own:
       U_i(bundle_i) >= U_i(bundle_k) for all agents i, k

   Envy from i to k: max(0, U_i(bundle_k) - U_i(bundle_i))

3. **Envy-Freeness up to one good (EF1)**:
   For indivisible goods: An allocation is EF1 if for any envious pair (i,k),
   removing one good from k's bundle eliminates i's envy.

   This is mainly relevant for discrete allocations. For divisible goods,
   we focus on standard envy-freeness.

4. **Proportionality**:
   Agent i gets at least their proportional share of the total welfare:
       U_i >= (w_i / sum_k w_k) * TotalUtility

   where w_i is agent i's entitlement weight and TotalUtility is the sum
   of all agents' utilities in the allocation.

5. **Symmetry**:
   If agents i and k have identical utility functions and identical entitlements,
   they should receive allocations that yield identical utilities.

USAGE:
------
    from fair_division import solve_nash_allocation, analyze_fairness

    result = solve_nash_allocation(utilities, entitlements)
    report = analyze_fairness(result.allocation, utilities, entitlements)
    print(report)
"""

from typing import Tuple, List
import numpy as np
import numpy.typing as npt

from .models import FairnessReport


def analyze_fairness(
    allocation: npt.NDArray[np.float64],
    utilities: npt.NDArray[np.float64],
    entitlements: npt.NDArray[np.float64],
    tolerance: float = 1e-6,
) -> FairnessReport:
    """
    Comprehensive fairness analysis of an allocation.

    This function evaluates the allocation against multiple fairness and
    efficiency criteria, returning a detailed report.

    Args:
        allocation: Allocation matrix of shape (n_agents, n_goods).
                    allocation[i,j] is the fraction of good j given to agent i.
        utilities: Utility matrix of shape (n_agents, n_goods).
                   utilities[i,j] is agent i's utility for good j.
        entitlements: Entitlement weights of shape (n_agents,).
        tolerance: Numerical tolerance for comparisons. Default: 1e-6.

    Returns:
        FairnessReport object containing detailed fairness metrics.

    Example:
        >>> allocation = np.array([[0.5, 0.5], [0.5, 0.5]])
        >>> utilities = np.array([[10, 5], [5, 10]])
        >>> entitlements = np.array([1.0, 1.0])
        >>> report = analyze_fairness(allocation, utilities, entitlements)
        >>> print(report.is_envy_free)
        True
    """
    n_agents, n_goods = allocation.shape

    # Compute realized utilities for each agent
    realized_utilities = (allocation * utilities).sum(axis=1)

    # Welfare metrics
    total_utility = realized_utilities.sum()
    min_utility = realized_utilities.min()

    # Nash welfare (geometric mean with weights)
    # Handle zero utilities carefully
    positive_utilities = np.maximum(realized_utilities, 1e-10)
    normalized_weights = entitlements / entitlements.sum()
    log_nash = (normalized_weights * np.log(positive_utilities)).sum()
    nash_welfare = np.exp(log_nash)

    # --- Pareto Efficiency Check ---
    # Heuristic: Check if any agent could be made better off by
    # reallocating goods without making others worse off.
    # This is a simplified check; full Pareto optimality requires solving
    # an optimization problem.
    is_pareto_efficient, pareto_note = _check_pareto_efficiency_heuristic(
        allocation, utilities, realized_utilities, tolerance
    )

    # --- Envy Analysis ---
    envy_matrix, max_envy, is_envy_free, envious_pairs = _analyze_envy(
        allocation, utilities, realized_utilities, tolerance
    )

    # --- Proportionality Analysis ---
    proportional_shares = (entitlements / entitlements.sum()) * total_utility
    proportionality_gaps = realized_utilities - proportional_shares
    is_proportional = np.all(proportionality_gaps >= -tolerance)

    # --- Symmetry Analysis ---
    is_symmetric_instance = _check_symmetric_instance(utilities, entitlements, tolerance)
    is_symmetric_allocation = _check_symmetric_allocation(
        allocation, realized_utilities, utilities, entitlements, tolerance
    )

    # --- Summary ---
    fairness_summary = {
        "overall_fairness_score": _compute_overall_fairness_score(
            is_pareto_efficient, is_envy_free, is_proportional, max_envy
        ),
        "num_envious_pairs": len(envious_pairs),
        "max_proportionality_gap": proportionality_gaps.min(),
        "welfare_concentration": _compute_welfare_concentration(realized_utilities),
    }

    return FairnessReport(
        utilities=realized_utilities,
        total_utility=total_utility,
        nash_welfare=nash_welfare,
        min_utility=min_utility,
        is_pareto_efficient=is_pareto_efficient,
        pareto_check_note=pareto_note,
        envy_matrix=envy_matrix,
        max_envy=max_envy,
        is_envy_free=is_envy_free,
        envious_pairs=envious_pairs,
        proportional_shares=proportional_shares,
        proportionality_gaps=proportionality_gaps,
        is_proportional=is_proportional,
        is_symmetric_instance=is_symmetric_instance,
        is_symmetric_allocation=is_symmetric_allocation,
        fairness_summary=fairness_summary,
    )


def _check_pareto_efficiency_heuristic(
    allocation: npt.NDArray[np.float64],
    utilities: npt.NDArray[np.float64],
    realized_utilities: npt.NDArray[np.float64],
    tolerance: float,
) -> Tuple[bool, str]:
    """
    Heuristic check for Pareto efficiency.

    This is NOT a complete check. We look for obvious inefficiencies:
    - Is there any good that is not fully allocated?
    - Is there a simple reallocation that improves someone without hurting anyone?

    Returns:
        (is_efficient, note) where note explains the determination.
    """
    n_agents, n_goods = allocation.shape

    # Check 1: All goods should be fully allocated
    col_sums = allocation.sum(axis=0)
    if not np.allclose(col_sums, 1.0, atol=tolerance):
        return False, "Goods not fully allocated"

    # Check 2: No agent should receive a good they value at 0 while another
    # agent values it positively and receives less than full allocation.
    for j in range(n_goods):
        for i in range(n_agents):
            if allocation[i, j] > tolerance and utilities[i, j] < tolerance:
                # Agent i gets good j but values it at ~0
                for k in range(n_agents):
                    if k != i and utilities[k, j] > tolerance and allocation[k, j] < 1.0 - tolerance:
                        # Agent k values good j but doesn't get all of it
                        # We could improve k without hurting i
                        return False, f"Good {j} allocated inefficiently (agent {i} values it 0, agent {k} values it positive)"

    # If no obvious inefficiency found, assume efficient (but this is not proof!)
    return True, "No obvious inefficiency detected (heuristic check)"


def _analyze_envy(
    allocation: npt.NDArray[np.float64],
    utilities: npt.NDArray[np.float64],
    realized_utilities: npt.NDArray[np.float64],
    tolerance: float,
) -> Tuple[npt.NDArray[np.float64], float, bool, List[Tuple[int, int, float]]]:
    """
    Analyze envy between agents.

    Returns:
        (envy_matrix, max_envy, is_envy_free, envious_pairs)
    """
    n_agents = len(realized_utilities)

    envy_matrix = np.zeros((n_agents, n_agents))
    envious_pairs = []

    for i in range(n_agents):
        for k in range(n_agents):
            if i == k:
                continue

            # What is agent i's utility for agent k's bundle?
            bundle_k = allocation[k, :]
            utility_i_for_k = (utilities[i, :] * bundle_k).sum()

            # Envy from i to k
            envy = utility_i_for_k - realized_utilities[i]
            envy_matrix[i, k] = max(0, envy)

            if envy > tolerance:
                envious_pairs.append((i, k, envy))

    max_envy = envy_matrix.max()
    is_envy_free = max_envy <= tolerance

    # Sort envious pairs by envy amount (descending)
    envious_pairs.sort(key=lambda x: x[2], reverse=True)

    return envy_matrix, max_envy, is_envy_free, envious_pairs


def _check_symmetric_instance(
    utilities: npt.NDArray[np.float64],
    entitlements: npt.NDArray[np.float64],
    tolerance: float,
) -> bool:
    """
    Check if the instance is symmetric: all agents have identical utilities and entitlements.
    """
    n_agents = utilities.shape[0]

    # Check if all utility rows are identical
    for i in range(1, n_agents):
        if not np.allclose(utilities[i, :], utilities[0, :], atol=tolerance):
            return False

    # Check if all entitlements are identical
    if not np.allclose(entitlements, entitlements[0], atol=tolerance):
        return False

    return True


def _check_symmetric_allocation(
    allocation: npt.NDArray[np.float64],
    realized_utilities: npt.NDArray[np.float64],
    utilities: npt.NDArray[np.float64],
    entitlements: npt.NDArray[np.float64],
    tolerance: float,
) -> bool:
    """
    Check if symmetric agents receive symmetric allocations.

    For each pair of agents with identical utilities and entitlements,
    check if they receive identical utilities.
    """
    n_agents = utilities.shape[0]

    for i in range(n_agents):
        for k in range(i + 1, n_agents):
            # Are agents i and k symmetric?
            if (
                np.allclose(utilities[i, :], utilities[k, :], atol=tolerance)
                and np.abs(entitlements[i] - entitlements[k]) <= tolerance
            ):
                # They should have equal utilities
                if np.abs(realized_utilities[i] - realized_utilities[k]) > tolerance:
                    return False

    return True


def _compute_overall_fairness_score(
    is_pareto_efficient: bool,
    is_envy_free: bool,
    is_proportional: bool,
    max_envy: float,
) -> str:
    """
    Compute a qualitative overall fairness score.
    """
    if is_pareto_efficient and is_envy_free and is_proportional:
        return "Excellent (Pareto + EF + Proportional)"
    elif is_pareto_efficient and is_envy_free:
        return "Very Good (Pareto + EF)"
    elif is_pareto_efficient and max_envy < 0.1:
        return "Good (Pareto + Low Envy)"
    elif is_pareto_efficient:
        return "Fair (Pareto Efficient)"
    elif is_envy_free:
        return "Fair (Envy-Free)"
    else:
        return "Limited (Some fairness issues)"


def _compute_welfare_concentration(utilities: npt.NDArray[np.float64]) -> float:
    """
    Compute the Gini coefficient of utilities as a measure of inequality.

    Returns a value in [0, 1] where 0 = perfect equality, 1 = maximal inequality.
    """
    if len(utilities) == 0:
        return 0.0

    sorted_utilities = np.sort(utilities)
    n = len(utilities)
    cumsum = np.cumsum(sorted_utilities)
    total = cumsum[-1]

    if total == 0:
        return 0.0

    # Gini coefficient formula
    gini = (2 * np.sum((np.arange(1, n + 1)) * sorted_utilities)) / (n * total) - (n + 1) / n

    return gini


def compute_envy_matrix(
    allocation: npt.NDArray[np.float64],
    utilities: npt.NDArray[np.float64],
) -> npt.NDArray[np.float64]:
    """
    Compute the envy matrix for an allocation.

    Args:
        allocation: Allocation matrix of shape (n_agents, n_goods).
        utilities: Utility matrix of shape (n_agents, n_goods).

    Returns:
        Envy matrix of shape (n_agents, n_agents) where entry [i,k] is
        max(0, U_i(bundle_k) - U_i(bundle_i)), i.e., how much agent i envies agent k.
    """
    n_agents = allocation.shape[0]
    realized_utilities = (allocation * utilities).sum(axis=1)
    envy_matrix = np.zeros((n_agents, n_agents))

    for i in range(n_agents):
        for k in range(n_agents):
            if i == k:
                continue
            bundle_k = allocation[k, :]
            utility_i_for_k = (utilities[i, :] * bundle_k).sum()
            envy_matrix[i, k] = max(0, utility_i_for_k - realized_utilities[i])

    return envy_matrix


def check_ef1(
    allocation: npt.NDArray[np.float64],
    utilities: npt.NDArray[np.float64],
    tolerance: float = 1e-6,
) -> bool:
    """
    Check if an allocation is EF1 (envy-free up to one good).

    This is mainly meaningful for discrete allocations where goods are
    indivisible and allocated in whole units.

    For each envious pair (i, k), check if removing any single good from
    k's bundle would eliminate i's envy.

    Args:
        allocation: Allocation matrix of shape (n_agents, n_goods).
                    For EF1, typically entries are 0 or 1 (discrete allocation).
        utilities: Utility matrix of shape (n_agents, n_goods).
        tolerance: Numerical tolerance.

    Returns:
        True if the allocation is EF1, False otherwise.
    """
    n_agents, n_goods = allocation.shape
    realized_utilities = (allocation * utilities).sum(axis=1)

    for i in range(n_agents):
        for k in range(n_agents):
            if i == k:
                continue

            # Does i envy k?
            bundle_k = allocation[k, :]
            utility_i_for_k = (utilities[i, :] * bundle_k).sum()

            if utility_i_for_k - realized_utilities[i] <= tolerance:
                # No envy
                continue

            # i envies k. Can we remove one good from k's bundle to eliminate envy?
            ef1_satisfied = False
            for j in range(n_goods):
                if bundle_k[j] > tolerance:
                    # Remove good j from k's bundle
                    reduced_bundle = bundle_k.copy()
                    reduced_bundle[j] = 0
                    utility_i_for_reduced = (utilities[i, :] * reduced_bundle).sum()

                    if utility_i_for_reduced - realized_utilities[i] <= tolerance:
                        # Envy eliminated
                        ef1_satisfied = True
                        break

            if not ef1_satisfied:
                # Could not eliminate envy for pair (i, k)
                return False

    return True
