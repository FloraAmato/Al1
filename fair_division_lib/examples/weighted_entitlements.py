"""
Weighted Entitlements Example

This example demonstrates how entitlement weights affect allocations
and validates the monotonicity property: increasing an agent's weight
should generally increase their utility.

GAME-THEORETIC PROPERTY TESTED:
- Monotonicity with respect to entitlements (Nash bargaining axiom)
"""

import numpy as np
from fair_division import (
    solve_maxmin_allocation,
    solve_nash_allocation,
    analyze_fairness,
)


def main():
    print("=" * 80)
    print("WEIGHTED ENTITLEMENTS EXAMPLE")
    print("=" * 80)
    print()
    print("This example shows how entitlement weights affect fair allocations.")
    print("An agent with higher entitlement should generally receive higher utility.")
    print()

    # Define utilities: 2 agents, 3 goods
    utilities = np.array([
        [10.0, 5.0, 8.0],
        [5.0, 10.0, 6.0],
    ])

    print("Utility Matrix:")
    print(utilities)
    print()

    # Test different entitlement scenarios
    scenarios = [
        ("Equal Entitlements", np.array([1.0, 1.0])),
        ("Agent 0 has 2x entitlement", np.array([2.0, 1.0])),
        ("Agent 1 has 3x entitlement", np.array([1.0, 3.0])),
    ]

    results_nash = []
    results_maxmin = []

    for scenario_name, entitlements in scenarios:
        print("-" * 80)
        print(f"SCENARIO: {scenario_name}")
        print("-" * 80)
        print(f"Entitlements: {entitlements}")
        print()

        # Nash allocation
        result_nash = solve_nash_allocation(utilities, entitlements)
        fairness_nash = analyze_fairness(result_nash.allocation, utilities, entitlements)

        print("NASH ALLOCATION:")
        print(f"  Agent 0 utility: {result_nash.utilities[0]:.4f}")
        print(f"  Agent 1 utility: {result_nash.utilities[1]:.4f}")
        print(f"  Ratio (U0/U1): {result_nash.utilities[0] / result_nash.utilities[1]:.4f}")
        print(f"  Envy-Free: {fairness_nash.is_envy_free}")
        print()

        # Max-min allocation
        result_maxmin = solve_maxmin_allocation(utilities, entitlements)
        fairness_maxmin = analyze_fairness(result_maxmin.allocation, utilities, entitlements)

        print("MAX-MIN ALLOCATION:")
        print(f"  Agent 0 utility: {result_maxmin.utilities[0]:.4f}")
        print(f"  Agent 1 utility: {result_maxmin.utilities[1]:.4f}")
        print(f"  Normalized U0: {result_maxmin.utilities[0] / entitlements[0]:.4f}")
        print(f"  Normalized U1: {result_maxmin.utilities[1] / entitlements[1]:.4f}")
        print(f"  Normalized utilities equal: {np.allclose(result_maxmin.utilities[0] / entitlements[0], result_maxmin.utilities[1] / entitlements[1], atol=1e-4)}")
        print()

        results_nash.append(result_nash)
        results_maxmin.append(result_maxmin)

    # --- MONOTONICITY ANALYSIS ---
    print("=" * 80)
    print("MONOTONICITY ANALYSIS (Nash Solution)")
    print("=" * 80)
    print()
    print("Property: Increasing an agent's entitlement should increase their utility.")
    print()

    # Compare scenarios
    equal_nash = results_nash[0]
    agent0_favored_nash = results_nash[1]
    agent1_favored_nash = results_nash[2]

    print("Agent 0's utility as their entitlement increases:")
    print(f"  w0=1.0: U0 = {equal_nash.utilities[0]:.4f}")
    print(f"  w0=2.0: U0 = {agent0_favored_nash.utilities[0]:.4f}")
    print()

    if agent0_favored_nash.utilities[0] > equal_nash.utilities[0]:
        print("✓ Monotonicity holds: Agent 0's utility increased when their entitlement increased")
    else:
        print("✗ Monotonicity violation (unusual, check instance)")
    print()

    print("Agent 1's utility as their entitlement increases:")
    print(f"  w1=1.0: U1 = {equal_nash.utilities[1]:.4f}")
    print(f"  w1=3.0: U1 = {agent1_favored_nash.utilities[1]:.4f}")
    print()

    if agent1_favored_nash.utilities[1] > equal_nash.utilities[1]:
        print("✓ Monotonicity holds: Agent 1's utility increased when their entitlement increased")
    else:
        print("✗ Monotonicity violation (unusual, check instance)")
    print()

    # --- MAX-MIN INTERPRETATION ---
    print("=" * 80)
    print("MAX-MIN INTERPRETATION")
    print("=" * 80)
    print()
    print("Max-min seeks to equalize NORMALIZED utilities (U_i / w_i).")
    print("This means agents with higher entitlements get proportionally more utility.")
    print()

    for i, (scenario_name, entitlements) in enumerate(scenarios):
        result = results_maxmin[i]
        print(f"{scenario_name}:")
        print(f"  Normalized utilities: {result.utilities / entitlements}")
        print()


if __name__ == "__main__":
    main()
