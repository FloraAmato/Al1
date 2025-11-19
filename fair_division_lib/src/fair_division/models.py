"""
Data models for fair division algorithms.

This module defines the core data structures used throughout the library.
"""

from dataclasses import dataclass, field
from typing import Dict, Optional, Tuple
import numpy as np
import numpy.typing as npt


@dataclass
class AllocationResult:
    """
    Result of a fair division algorithm.

    Attributes:
        allocation: Matrix x[i,j] representing the fraction of good j allocated to agent i.
                   Shape: (n_agents, n_goods). Each column sums to 1.0.
        utilities: Array of total utilities achieved by each agent. Shape: (n_agents,).
        objective_value: The value of the optimization objective (max-min utility or Nash product).
        solver_status: String indicating solver status ('optimal', 'feasible', 'infeasible', etc.).
        solve_time: Time in seconds to solve the optimization problem.
        metadata: Additional solver-specific information.
    """
    allocation: npt.NDArray[np.float64]
    utilities: npt.NDArray[np.float64]
    objective_value: float
    solver_status: str
    solve_time: float
    metadata: Dict = field(default_factory=dict)

    def __post_init__(self):
        """Validate the allocation result."""
        n_agents, n_goods = self.allocation.shape

        # Check that allocation is non-negative
        if np.any(self.allocation < -1e-9):
            raise ValueError("Allocation contains negative values")

        # Check that each good is fully allocated (each column sums to ~1)
        col_sums = self.allocation.sum(axis=0)
        if not np.allclose(col_sums, 1.0, atol=1e-6):
            raise ValueError(f"Goods not fully allocated. Column sums: {col_sums}")

        # Check utilities array shape
        if self.utilities.shape != (n_agents,):
            raise ValueError(f"Utilities shape {self.utilities.shape} doesn't match n_agents={n_agents}")


@dataclass
class FairnessReport:
    """
    Comprehensive fairness analysis of an allocation.

    This report evaluates the allocation against standard game-theoretic fairness
    and efficiency criteria.

    Attributes:
        utilities: Per-agent realized utilities. Shape: (n_agents,).
        total_utility: Sum of all agent utilities (utilitarian welfare).
        nash_welfare: Geometric mean of utilities (Nash social welfare).
        min_utility: Minimum utility (egalitarian welfare).

        # Pareto Efficiency
        is_pareto_efficient: True if no obvious Pareto improvements found (heuristic check).
        pareto_check_note: Explanation of Pareto efficiency determination.

        # Envy Analysis
        envy_matrix: Matrix where entry [i,k] = max(0, U_k - U_i), i.e.,
                     how much agent i envies agent k. Shape: (n_agents, n_agents).
        max_envy: Maximum envy value across all agent pairs.
        is_envy_free: True if max_envy ≈ 0 (within tolerance).
        envious_pairs: List of (i, k, envy_amount) tuples where agent i envies k.

        # Proportionality
        proportional_shares: For each agent i, their proportional share = w_i / sum(w) * total_utility.
        proportionality_gaps: For each agent i, U_i - proportional_share[i].
        is_proportional: True if all agents get at least their proportional share.

        # Symmetry
        is_symmetric_instance: True if all agents have identical utilities and entitlements.
        is_symmetric_allocation: True if allocation treats symmetric agents identically.

        # Summary
        fairness_summary: Dict with high-level fairness flags and metrics.
    """
    # Welfare metrics
    utilities: npt.NDArray[np.float64]
    total_utility: float
    nash_welfare: float
    min_utility: float

    # Pareto efficiency
    is_pareto_efficient: bool
    pareto_check_note: str

    # Envy analysis
    envy_matrix: npt.NDArray[np.float64]
    max_envy: float
    is_envy_free: bool
    envious_pairs: list[Tuple[int, int, float]]

    # Proportionality
    proportional_shares: npt.NDArray[np.float64]
    proportionality_gaps: npt.NDArray[np.float64]
    is_proportional: bool

    # Symmetry
    is_symmetric_instance: bool
    is_symmetric_allocation: bool

    # Summary
    fairness_summary: Dict = field(default_factory=dict)

    def __str__(self) -> str:
        """Human-readable fairness report."""
        lines = [
            "=" * 70,
            "FAIRNESS ANALYSIS REPORT",
            "=" * 70,
            "",
            "WELFARE METRICS",
            "-" * 70,
            f"  Utilities:         {self.utilities}",
            f"  Total Utility:     {self.total_utility:.4f}",
            f"  Nash Welfare:      {self.nash_welfare:.4f}",
            f"  Min Utility:       {self.min_utility:.4f}",
            "",
            "PARETO EFFICIENCY",
            "-" * 70,
            f"  Status:            {'✓ Efficient' if self.is_pareto_efficient else '✗ Not verified'}",
            f"  Note:              {self.pareto_check_note}",
            "",
            "ENVY ANALYSIS",
            "-" * 70,
            f"  Envy-Free:         {'✓ Yes' if self.is_envy_free else '✗ No'}",
            f"  Max Envy:          {self.max_envy:.4f}",
        ]

        if self.envious_pairs:
            lines.append("  Envious Pairs:")
            for i, k, envy in self.envious_pairs[:5]:  # Show top 5
                lines.append(f"    Agent {i} → Agent {k}: {envy:.4f}")
            if len(self.envious_pairs) > 5:
                lines.append(f"    ... and {len(self.envious_pairs) - 5} more")

        lines.extend([
            "",
            "PROPORTIONALITY",
            "-" * 70,
            f"  Proportional:      {'✓ Yes' if self.is_proportional else '✗ No'}",
            f"  Proportional Shares: {self.proportional_shares}",
            f"  Gaps (U - share):  {self.proportionality_gaps}",
            "",
            "SYMMETRY",
            "-" * 70,
            f"  Symmetric Instance:   {'Yes' if self.is_symmetric_instance else 'No'}",
            f"  Symmetric Allocation: {'✓ Yes' if self.is_symmetric_allocation else '✗ No'}",
            "",
            "SUMMARY",
            "-" * 70,
        ])

        for key, value in self.fairness_summary.items():
            lines.append(f"  {key}: {value}")

        lines.append("=" * 70)
        return "\n".join(lines)
