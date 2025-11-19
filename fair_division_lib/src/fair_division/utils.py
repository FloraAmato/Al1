"""
Utility functions for fair division algorithms.
"""

import numpy as np
import numpy.typing as npt
from typing import Tuple


def validate_inputs(
    utilities: npt.NDArray[np.float64],
    entitlements: npt.NDArray[np.float64],
) -> Tuple[int, int]:
    """
    Validate utility matrix and entitlements.

    Args:
        utilities: Utility matrix of shape (n_agents, n_goods).
        entitlements: Entitlement weights of shape (n_agents,).

    Returns:
        Tuple (n_agents, n_goods)

    Raises:
        ValueError: If inputs are invalid.
    """
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

    return n_agents, n_goods


def normalize_allocation(
    allocation: npt.NDArray[np.float64],
    tolerance: float = 1e-9,
) -> npt.NDArray[np.float64]:
    """
    Normalize allocation so each good is fully allocated.

    This function adjusts allocation columns to sum to exactly 1.0,
    useful for correcting small numerical errors.

    Args:
        allocation: Allocation matrix of shape (n_agents, n_goods).
        tolerance: Tolerance for checking if normalization is needed.

    Returns:
        Normalized allocation matrix.
    """
    allocation = allocation.copy()
    n_agents, n_goods = allocation.shape

    for j in range(n_goods):
        col_sum = allocation[:, j].sum()
        if abs(col_sum - 1.0) > tolerance:
            if col_sum > tolerance:
                allocation[:, j] /= col_sum
            else:
                # If column sums to ~0, distribute equally
                allocation[:, j] = 1.0 / n_agents

    return allocation


def generate_random_utilities(
    n_agents: int,
    n_goods: int,
    low: float = 0.0,
    high: float = 10.0,
    seed: int = None,
) -> npt.NDArray[np.float64]:
    """
    Generate random utility matrix for testing.

    Args:
        n_agents: Number of agents.
        n_goods: Number of goods.
        low: Lower bound for utilities.
        high: Upper bound for utilities.
        seed: Random seed for reproducibility.

    Returns:
        Random utility matrix of shape (n_agents, n_goods).
    """
    if seed is not None:
        np.random.seed(seed)
    return np.random.uniform(low, high, (n_agents, n_goods))


def generate_symmetric_utilities(
    n_agents: int,
    utilities_per_agent: npt.NDArray[np.float64],
) -> npt.NDArray[np.float64]:
    """
    Generate symmetric utility matrix where all agents have identical utilities.

    Args:
        n_agents: Number of agents.
        utilities_per_agent: Utility vector of shape (n_goods,) to replicate for each agent.

    Returns:
        Utility matrix of shape (n_agents, n_goods) where each row is identical.
    """
    n_goods = len(utilities_per_agent)
    return np.tile(utilities_per_agent, (n_agents, 1))
