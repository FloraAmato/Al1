"""
Tests for max-min fair allocation solver.
"""

import pytest
import numpy as np
from fair_division import solve_maxmin_allocation, analyze_fairness


class TestMaxMinSolver:
    """Test suite for max-min allocation solver."""

    def test_basic_feasibility(self):
        """Test that solver produces a feasible allocation."""
        utilities = np.array([
            [10.0, 5.0],
            [5.0, 10.0],
        ])
        entitlements = np.array([1.0, 1.0])

        result = solve_maxmin_allocation(utilities, entitlements)

        assert result.solver_status == "optimal"
        assert result.allocation.shape == (2, 2)

        # Check that goods are fully allocated
        assert np.allclose(result.allocation.sum(axis=0), 1.0)

        # Check non-negativity
        assert np.all(result.allocation >= -1e-9)

    def test_symmetric_instance_produces_equal_utilities(self):
        """Test symmetry axiom: symmetric agents should get equal utilities."""
        # All agents have identical utilities
        common_utils = np.array([10.0, 5.0, 8.0])
        utilities = np.tile(common_utils, (3, 1))
        entitlements = np.array([1.0, 1.0, 1.0])

        result = solve_maxmin_allocation(utilities, entitlements)

        # All agents should get equal utility
        assert np.allclose(result.utilities, result.utilities[0], atol=1e-4)

        # Check fairness report
        fairness = analyze_fairness(result.allocation, utilities, entitlements)
        assert fairness.is_symmetric_instance
        assert fairness.is_symmetric_allocation

    def test_normalized_utilities_are_equal(self):
        """Test that max-min equalizes normalized utilities U_i / w_i."""
        utilities = np.array([
            [10.0, 5.0],
            [5.0, 10.0],
        ])
        entitlements = np.array([2.0, 1.0])

        result = solve_maxmin_allocation(utilities, entitlements)

        # Normalized utilities should be equal
        normalized = result.utilities / entitlements
        assert np.allclose(normalized, normalized[0], atol=1e-4)

    def test_pareto_efficiency_simple_case(self):
        """Test Pareto efficiency in a simple case."""
        # Agent 0 values good 0 highly, agent 1 values good 1 highly
        utilities = np.array([
            [10.0, 1.0],
            [1.0, 10.0],
        ])
        entitlements = np.array([1.0, 1.0])

        result = solve_maxmin_allocation(utilities, entitlements)

        # In this case, efficient allocation is close to:
        # Agent 0 gets most of good 0, Agent 1 gets most of good 1
        # But max-min also balances utilities

        fairness = analyze_fairness(result.allocation, utilities, entitlements)
        # Should be Pareto efficient (heuristic check)
        assert fairness.is_pareto_efficient

    def test_input_validation(self):
        """Test that invalid inputs raise errors."""
        # Negative utilities
        with pytest.raises(ValueError, match="non-negative"):
            solve_maxmin_allocation(
                np.array([[10, -5], [5, 10]]),
                np.array([1.0, 1.0])
            )

        # Zero entitlements
        with pytest.raises(ValueError, match="strictly positive"):
            solve_maxmin_allocation(
                np.array([[10, 5], [5, 10]]),
                np.array([0.0, 1.0])
            )

        # Mismatched shapes
        with pytest.raises(ValueError):
            solve_maxmin_allocation(
                np.array([[10, 5], [5, 10]]),
                np.array([1.0, 1.0, 1.0])  # 3 entitlements for 2 agents
            )

    def test_single_agent(self):
        """Test allocation with a single agent."""
        utilities = np.array([[10.0, 5.0, 8.0]])
        entitlements = np.array([1.0])

        result = solve_maxmin_allocation(utilities, entitlements)

        # Single agent should get everything
        assert np.allclose(result.allocation[0, :], 1.0)
        assert np.isclose(result.utilities[0], 23.0)

    def test_zero_utility_good(self):
        """Test handling of a good with zero utility for all agents."""
        utilities = np.array([
            [10.0, 0.0, 5.0],
            [5.0, 0.0, 10.0],
        ])
        entitlements = np.array([1.0, 1.0])

        result = solve_maxmin_allocation(utilities, entitlements)

        assert result.solver_status == "optimal"
        # Allocation for good 1 (zero utility) can be arbitrary
        # but other goods should be allocated sensibly


class TestMaxMinGameTheoreticProperties:
    """Test game-theoretic properties of max-min solver."""

    def test_monotonicity_wrt_entitlements(self):
        """Test that increasing entitlement increases utility."""
        utilities = np.array([
            [10.0, 5.0, 8.0],
            [6.0, 9.0, 7.0],
        ])

        # Baseline: equal entitlements
        entitlements_equal = np.array([1.0, 1.0])
        result_equal = solve_maxmin_allocation(utilities, entitlements_equal)

        # Increase agent 0's entitlement
        entitlements_favored = np.array([2.0, 1.0])
        result_favored = solve_maxmin_allocation(utilities, entitlements_favored)

        # Agent 0's utility should increase (or at least not decrease significantly)
        # Note: monotonicity in max-min is w.r.t. normalized utilities,
        # so U_0 should roughly double
        assert result_favored.utilities[0] >= result_equal.utilities[0] - 1e-4

    def test_independence_of_scaling(self):
        """Test that scaling all utilities by a constant doesn't change allocation."""
        utilities = np.array([
            [10.0, 5.0],
            [5.0, 10.0],
        ])
        entitlements = np.array([1.0, 1.0])

        result1 = solve_maxmin_allocation(utilities, entitlements)

        # Scale utilities by 10
        utilities_scaled = utilities * 10
        result2 = solve_maxmin_allocation(utilities_scaled, entitlements)

        # Allocations should be identical
        assert np.allclose(result1.allocation, result2.allocation, atol=1e-4)

        # Utilities should scale proportionally
        assert np.allclose(result2.utilities, result1.utilities * 10, rtol=1e-3)
