"""
Symmetric Instance Example

This example demonstrates how both solvers handle symmetric instances
where all agents have identical utilities and entitlements.

EXPECTED BEHAVIOR:
- Both solvers should produce symmetric allocations (equal utilities)
- Allocations should be envy-free
- Allocations should be Pareto efficient
"""

import numpy as np
from fair_division import (
    solve_maxmin_allocation,
    solve_nash_allocation,
    analyze_fairness,
)


def main():
    print("=" * 80)
    print("SYMMETRIC INSTANCE EXAMPLE")
    print("=" * 80)
    print()
    print("In a symmetric instance, all agents have identical utility functions")
    print("and identical entitlements. Game theory predicts that fair solutions")
    print("should give all agents equal utilities (symmetry axiom).")
    print()

    # Create a symmetric instance: 3 agents, 4 goods
    # All agents have the same utility function
    common_utilities = np.array([10.0, 7.0, 8.0, 5.0])
    utilities = np.tile(common_utilities, (3, 1))  # Repeat for 3 agents

    entitlements = np.array([1.0, 1.0, 1.0])  # Equal entitlements

    print("Utility Matrix (all agents identical):")
    print(utilities)
    print()
    print("Entitlements (all equal):", entitlements)
    print()

    # --- MAX-MIN ALLOCATION ---
    print("-" * 80)
    print("MAX-MIN ALLOCATION")
    print("-" * 80)

    result_maxmin = solve_maxmin_allocation(utilities, entitlements)
    fairness_maxmin = analyze_fairness(result_maxmin.allocation, utilities, entitlements)

    print(f"Solver Status: {result_maxmin.solver_status}")
    print()
    print("Agent Utilities:", result_maxmin.utilities)
    print(f"Utilities are equal: {np.allclose(result_maxmin.utilities, result_maxmin.utilities[0])}")
    print()
    print(f"Symmetric Instance: {fairness_maxmin.is_symmetric_instance}")
    print(f"Symmetric Allocation: {fairness_maxmin.is_symmetric_allocation}")
    print(f"Envy-Free: {fairness_maxmin.is_envy_free}")
    print(f"Max Envy: {fairness_maxmin.max_envy:.6f}")
    print()

    # --- NASH ALLOCATION ---
    print("-" * 80)
    print("NASH ALLOCATION")
    print("-" * 80)

    result_nash = solve_nash_allocation(utilities, entitlements)
    fairness_nash = analyze_fairness(result_nash.allocation, utilities, entitlements)

    print(f"Solver Status: {result_nash.solver_status}")
    print()
    print("Agent Utilities:", result_nash.utilities)
    print(f"Utilities are equal: {np.allclose(result_nash.utilities, result_nash.utilities[0])}")
    print()
    print(f"Symmetric Instance: {fairness_nash.is_symmetric_instance}")
    print(f"Symmetric Allocation: {fairness_nash.is_symmetric_allocation}")
    print(f"Envy-Free: {fairness_nash.is_envy_free}")
    print(f"Max Envy: {fairness_nash.max_envy:.6f}")
    print()

    # --- VERIFICATION ---
    print("-" * 80)
    print("SYMMETRY VERIFICATION")
    print("-" * 80)
    print()
    print("Both algorithms should satisfy the SYMMETRY axiom:")
    print("  If all agents are identical, they should receive equal utilities.")
    print()
    print(f"Max-Min satisfies symmetry: {fairness_maxmin.is_symmetric_allocation}")
    print(f"Nash satisfies symmetry: {fairness_nash.is_symmetric_allocation}")
    print()

    if fairness_maxmin.is_symmetric_allocation and fairness_nash.is_symmetric_allocation:
        print("✓ SUCCESS: Both algorithms respect symmetry!")
    else:
        print("✗ WARNING: Symmetry violation detected (may be due to numerical precision)")
    print()


if __name__ == "__main__":
    main()
