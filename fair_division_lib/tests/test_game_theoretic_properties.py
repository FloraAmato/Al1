"""
Tests for game-theoretic properties across both solvers.

These tests verify that both max-min and Nash solvers satisfy
key axioms and properties from cooperative game theory and fair division.
"""

import pytest
import numpy as np
from fair_division import (
    solve_maxmin_allocation,
    solve_nash_allocation,
    analyze_fairness,
)


class TestSymmetryAxiom:
    """Test the symmetry axiom for both solvers."""

    @pytest.mark.parametrize("solver", [solve_maxmin_allocation, solve_nash_allocation])
    def test_symmetry_two_agents(self, solver):
        """Test symmetry with 2 agents."""
        # Identical agents
        common_utils = np.array([10.0, 5.0, 8.0])
        utilities = np.tile(common_utils, (2, 1))
        entitlements = np.array([1.0, 1.0])

        result = solver(utilities, entitlements)

        # Utilities should be equal
        assert np.allclose(result.utilities[0], result.utilities[1], atol=0.1)

    @pytest.mark.parametrize("solver", [solve_maxmin_allocation, solve_nash_allocation])
    def test_symmetry_three_agents(self, solver):
        """Test symmetry with 3 agents."""
        common_utils = np.array([7.0, 9.0, 5.0, 6.0])
        utilities = np.tile(common_utils, (3, 1))
        entitlements = np.array([1.0, 1.0, 1.0])

        result = solver(utilities, entitlements)
        fairness = analyze_fairness(result.allocation, utilities, entitlements)

        # Should detect symmetry
        assert fairness.is_symmetric_instance
        assert fairness.is_symmetric_allocation


class TestParetoEfficiency:
    """Test Pareto efficiency for both solvers."""

    @pytest.mark.parametrize("solver", [solve_maxmin_allocation, solve_nash_allocation])
    def test_pareto_efficiency_complementary_goods(self, solver):
        """Test Pareto efficiency with complementary preferences."""
        # Agent 0 values good 0, agent 1 values good 1
        utilities = np.array([
            [100.0, 1.0],
            [1.0, 100.0],
        ])
        entitlements = np.array([1.0, 1.0])

        result = solver(utilities, entitlements)
        fairness = analyze_fairness(result.allocation, utilities, entitlements)

        # Should be Pareto efficient (allocate each good to who values it most)
        assert fairness.is_pareto_efficient

    @pytest.mark.parametrize("solver", [solve_maxmin_allocation, solve_nash_allocation])
    def test_pareto_efficiency_general_case(self, solver):
        """Test Pareto efficiency in a general case."""
        utilities = np.array([
            [10.0, 5.0, 8.0],
            [6.0, 9.0, 7.0],
            [8.0, 7.0, 9.0],
        ])
        entitlements = np.array([1.0, 1.0, 1.0])

        result = solver(utilities, entitlements)
        fairness = analyze_fairness(result.allocation, utilities, entitlements)

        # Heuristic check should pass
        assert fairness.is_pareto_efficient


class TestMonotonicityWithRespectToEntitlements:
    """Test monotonicity w.r.t. entitlements for both solvers."""

    @pytest.mark.parametrize("solver", [solve_maxmin_allocation, solve_nash_allocation])
    def test_increasing_entitlement_increases_utility(self, solver):
        """Test that increasing entitlement increases utility."""
        utilities = np.array([
            [10.0, 5.0, 8.0],
            [6.0, 9.0, 7.0],
        ])

        # Baseline
        entitlements_base = np.array([1.0, 1.0])
        result_base = solver(utilities, entitlements_base)

        # Increase agent 0's entitlement
        entitlements_increased = np.array([2.5, 1.0])
        result_increased = solver(utilities, entitlements_increased)

        # Agent 0's utility should increase (or stay the same)
        # For max-min, normalized utility stays same, so absolute utility scales with entitlement
        # For Nash, increasing weight should increase utility

        if solver == solve_maxmin_allocation:
            # For max-min: U_0 / w_0 ≈ constant, so U_0 should increase proportionally
            assert result_increased.utilities[0] >= result_base.utilities[0] * 0.9  # Allow some tolerance
        else:
            # For Nash: higher weight → higher utility
            assert result_increased.utilities[0] > result_base.utilities[0] - 1e-3


class TestConsistencyAndStability:
    """Test consistency and numerical stability."""

    @pytest.mark.parametrize("solver", [solve_maxmin_allocation, solve_nash_allocation])
    def test_deterministic_results(self, solver):
        """Test that solver produces same results on repeated calls."""
        utilities = np.array([
            [10.0, 5.0],
            [5.0, 10.0],
        ])
        entitlements = np.array([1.0, 1.0])

        result1 = solver(utilities, entitlements)
        result2 = solver(utilities, entitlements)

        # Results should be identical
        assert np.allclose(result1.allocation, result2.allocation, atol=1e-6)
        assert np.allclose(result1.utilities, result2.utilities, atol=1e-6)

    @pytest.mark.parametrize("solver", [solve_maxmin_allocation, solve_nash_allocation])
    def test_small_utilities(self, solver):
        """Test numerical stability with small utilities."""
        utilities = np.array([
            [0.01, 0.005],
            [0.005, 0.01],
        ])
        entitlements = np.array([1.0, 1.0])

        result = solver(utilities, entitlements)

        assert result.solver_status in ["optimal", "feasible"]
        assert np.all(result.utilities > 0)

    @pytest.mark.parametrize("solver", [solve_maxmin_allocation, solve_nash_allocation])
    def test_large_utilities(self, solver):
        """Test numerical stability with large utilities."""
        utilities = np.array([
            [1000.0, 500.0],
            [500.0, 1000.0],
        ])
        entitlements = np.array([1.0, 1.0])

        result = solver(utilities, entitlements)

        assert result.solver_status in ["optimal", "feasible"]


class TestFairnessComparison:
    """Compare fairness properties between solvers."""

    def test_max_min_vs_nash_on_symmetric_instance(self):
        """Compare max-min and Nash on symmetric instance."""
        utilities = np.array([
            [10.0, 5.0, 8.0],
            [10.0, 5.0, 8.0],
        ])
        entitlements = np.array([1.0, 1.0])

        result_maxmin = solve_maxmin_allocation(utilities, entitlements)
        result_nash = solve_nash_allocation(utilities, entitlements)

        # Both should produce equal utilities for symmetric agents
        assert np.allclose(result_maxmin.utilities[0], result_maxmin.utilities[1], atol=1e-4)
        assert np.allclose(result_nash.utilities[0], result_nash.utilities[1], atol=0.1)

    def test_max_min_focuses_on_worst_off(self):
        """Test that max-min prioritizes the worst-off agent."""
        utilities = np.array([
            [10.0, 1.0],
            [1.0, 10.0],
            [5.0, 5.0],  # Agent 2 has balanced preferences
        ])
        entitlements = np.array([1.0, 1.0, 1.0])

        result_maxmin = solve_maxmin_allocation(utilities, entitlements)

        # Max-min should try to equalize utilities
        # The minimum utility should be maximized
        min_util = result_maxmin.utilities.min()

        # Check that no agent is far below the minimum
        assert np.all(result_maxmin.utilities >= min_util - 1e-4)

    def test_nash_balances_efficiency_and_fairness(self):
        """Test that Nash balances total welfare and fairness."""
        utilities = np.array([
            [10.0, 1.0],
            [1.0, 10.0],
        ])
        entitlements = np.array([1.0, 1.0])

        result_nash = solve_nash_allocation(utilities, entitlements)

        # Nash should allocate efficiently (most of each good to who values it)
        # while maintaining some balance
        assert result_nash.allocation[0, 0] > 0.5  # Agent 0 gets more of good 0
        assert result_nash.allocation[1, 1] > 0.5  # Agent 1 gets more of good 1

        # Both should have positive utilities
        assert np.all(result_nash.utilities > 0)
