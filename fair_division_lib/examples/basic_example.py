"""
Basic Example: Fair Division with Nash and Max-Min Solvers

This example demonstrates the basic usage of both solvers and
the fairness diagnostics module.
"""

import numpy as np
from fair_division import (
    solve_maxmin_allocation,
    solve_nash_allocation,
    analyze_fairness,
)


def main():
    print("=" * 80)
    print("BASIC FAIR DIVISION EXAMPLE")
    print("=" * 80)
    print()

    # Define a simple instance: 2 agents, 3 goods
    utilities = np.array([
        [10.0, 5.0, 8.0],   # Agent 0's utilities
        [5.0, 10.0, 6.0],   # Agent 1's utilities
    ])

    entitlements = np.array([1.0, 1.0])  # Equal entitlements

    print("Utility Matrix:")
    print(utilities)
    print()
    print("Entitlements:", entitlements)
    print()

    # --- MAX-MIN ALLOCATION ---
    print("-" * 80)
    print("MAX-MIN FAIR ALLOCATION (Egalitarian Solution)")
    print("-" * 80)

    result_maxmin = solve_maxmin_allocation(utilities, entitlements)

    print(f"Solver Status: {result_maxmin.solver_status}")
    print(f"Solve Time: {result_maxmin.solve_time:.4f}s")
    print()
    print("Allocation Matrix:")
    print(result_maxmin.allocation)
    print()
    print("Agent Utilities:", result_maxmin.utilities)
    print(f"Min Utility: {result_maxmin.utilities.min():.4f}")
    print(f"Objective (min normalized utility): {result_maxmin.objective_value:.4f}")
    print()

    # Analyze fairness
    fairness_maxmin = analyze_fairness(result_maxmin.allocation, utilities, entitlements)
    print(fairness_maxmin)
    print()

    # --- NASH ALLOCATION ---
    print("-" * 80)
    print("NASH SOCIAL WELFARE ALLOCATION (Nash Bargaining Solution)")
    print("-" * 80)

    result_nash = solve_nash_allocation(utilities, entitlements)

    print(f"Solver Status: {result_nash.solver_status}")
    print(f"Solve Time: {result_nash.solve_time:.4f}s")
    print()
    print("Allocation Matrix:")
    print(result_nash.allocation)
    print()
    print("Agent Utilities:", result_nash.utilities)
    print(f"Nash Welfare (log): {result_nash.objective_value:.4f}")
    print(f"Nash Welfare (product): {result_nash.metadata['nash_product']:.4f}")
    print()

    # Analyze fairness
    fairness_nash = analyze_fairness(result_nash.allocation, utilities, entitlements)
    print(fairness_nash)
    print()

    # --- COMPARISON ---
    print("-" * 80)
    print("COMPARISON")
    print("-" * 80)
    print(f"{'Metric':<30} {'Max-Min':<15} {'Nash':<15}")
    print("-" * 60)
    print(f"{'Min Utility':<30} {result_maxmin.utilities.min():<15.4f} {result_nash.utilities.min():<15.4f}")
    print(f"{'Total Utility':<30} {result_maxmin.utilities.sum():<15.4f} {result_nash.utilities.sum():<15.4f}")
    print(f"{'Nash Welfare':<30} {fairness_maxmin.nash_welfare:<15.4f} {fairness_nash.nash_welfare:<15.4f}")
    print(f"{'Max Envy':<30} {fairness_maxmin.max_envy:<15.4f} {fairness_nash.max_envy:<15.4f}")
    print(f"{'Envy-Free?':<30} {str(fairness_maxmin.is_envy_free):<15} {str(fairness_nash.is_envy_free):<15}")
    print(f"{'Proportional?':<30} {str(fairness_maxmin.is_proportional):<15} {str(fairness_nash.is_proportional):<15}")
    print()


if __name__ == "__main__":
    main()
