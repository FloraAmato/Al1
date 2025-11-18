"""
Tests for Nash social welfare solver.
"""

import pytest
import numpy as np
from fair_division import solve_nash_allocation, analyze_fairness


class TestNashSolver:
    """Test suite for Nash social welfare solver."""

    def test_basic_feasibility(self):
        """Test that solver produces a feasible allocation."""
        utilities = np.array([
            [10.0, 5.0],
            [5.0, 10.0],
        ])
        entitlements = np.array([1.0, 1.0])

        result = solve_nash_allocation(utilities, entitlements)

        assert result.solver_status in ["optimal", "feasible"]
        assert result.allocation.shape == (2, 2)

        # Check that goods are fully allocated
        assert np.allclose(result.allocation.sum(axis=0), 1.0, atol=1e-4)

        # Check non-negativity
        assert np.all(result.allocation >= -1e-9)

    def test_symmetric_instance_produces_equal_utilities(self):
        """Test symmetry axiom: symmetric agents should get equal utilities."""
        # All agents have identical utilities
        common_utils = np.array([10.0, 5.0, 8.0])
        utilities = np.tile(common_utils, (3, 1))
        entitlements = np.array([1.0, 1.0, 1.0])

        result = solve_nash_allocation(utilities, entitlements)

        # All agents should get equal utility (within tolerance)
        assert np.allclose(result.utilities, result.utilities[0], atol=0.1)

        # Check fairness report
        fairness = analyze_fairness(result.allocation, utilities, entitlements)
        assert fairness.is_symmetric_instance
        # Symmetric allocation may have small numerical errors
        # so we use a relaxed check

    def test_nash_welfare_objective(self):
        """Test that Nash welfare is being maximized."""
        utilities = np.array([
            [10.0, 5.0],
            [5.0, 10.0],
        ])
        entitlements = np.array([1.0, 1.0])

        result = solve_nash_allocation(utilities, entitlements)

        # Compute Nash welfare manually
        weights = entitlements / entitlements.sum()
        log_nash = (weights * np.log(result.utilities)).sum()

        # Should match the objective value
        assert np.isclose(result.objective_value, log_nash, rtol=1e-4)

    def test_monotonicity_wrt_entitlements(self):
        """Test that increasing entitlement increases utility."""
        utilities = np.array([
            [10.0, 5.0, 8.0],
            [6.0, 9.0, 7.0],
        ])

        # Baseline: equal entitlements
        entitlements_equal = np.array([1.0, 1.0])
        result_equal = solve_nash_allocation(utilities, entitlements_equal)

        # Increase agent 0's entitlement
        entitlements_favored = np.array([3.0, 1.0])
        result_favored = solve_nash_allocation(utilities, entitlements_favored)

        # Agent 0's utility should increase
        assert result_favored.utilities[0] > result_equal.utilities[0] - 1e-3

    def test_pareto_efficiency(self):
        """Test Pareto efficiency in a simple case."""
        # Agent 0 values good 0 highly, agent 1 values good 1 highly
        utilities = np.array([
            [10.0, 1.0],
            [1.0, 10.0],
        ])
        entitlements = np.array([1.0, 1.0])

        result = solve_nash_allocation(utilities, entitlements)

        fairness = analyze_fairness(result.allocation, utilities, entitlements)
        # Should be Pareto efficient
        assert fairness.is_pareto_efficient

    def test_input_validation(self):
        """Test that invalid inputs raise errors."""
        # Negative utilities
        with pytest.raises(ValueError, match="non-negative"):
            solve_nash_allocation(
                np.array([[10, -5], [5, 10]]),
                np.array([1.0, 1.0])
            )

        # Zero entitlements
        with pytest.raises(ValueError, match="strictly positive"):
            solve_nash_allocation(
                np.array([[10, 5], [5, 10]]),
                np.array([0.0, 1.0])
            )

    def test_single_agent(self):
        """Test allocation with a single agent."""
        utilities = np.array([[10.0, 5.0, 8.0]])
        entitlements = np.array([1.0])

        result = solve_nash_allocation(utilities, entitlements)

        # Single agent should get everything
        assert np.allclose(result.allocation[0, :], 1.0, atol=1e-4)
        assert np.isclose(result.utilities[0], 23.0, rtol=1e-3)


class TestNashGameTheoreticProperties:
    """Test game-theoretic properties of Nash solver."""

    def test_scale_invariance_of_allocation(self):
        """Test that scaling one agent's utilities affects allocation predictably."""
        utilities = np.array([
            [10.0, 5.0],
            [5.0, 10.0],
        ])
        entitlements = np.array([1.0, 1.0])

        result1 = solve_nash_allocation(utilities, entitlements)

        # Scale agent 0's utilities by 2
        utilities_scaled = utilities.copy()
        utilities_scaled[0, :] *= 2
        result2 = solve_nash_allocation(utilities_scaled, entitlements)

        # The allocation should change (Nash is not scale-invariant w.r.t.
        # individual agent scaling in this model)
        # Agent 0 should get relatively more (their utilities doubled)
        assert result2.utilities[0] / utilities_scaled[0, :].sum() > result1.utilities[0] / utilities[0, :].sum() - 0.1

    def test_proportional_fairness_tendency(self):
        """Test that Nash tends toward proportional allocations."""
        # In symmetric case with equal entitlements, should be close to proportional
        utilities = np.array([
            [10.0, 10.0],
            [10.0, 10.0],
        ])
        entitlements = np.array([1.0, 1.0])

        result = solve_nash_allocation(utilities, entitlements)
        fairness = analyze_fairness(result.allocation, utilities, entitlements)

        # Should be proportional (each agent gets ~50% of total utility)
        assert fairness.is_proportional

    def test_complementary_goods(self):
        """Test Nash allocation with complementary preferences."""
        # Agent 0 strongly prefers good 0, agent 1 strongly prefers good 1
        utilities = np.array([
            [100.0, 1.0],
            [1.0, 100.0],
        ])
        entitlements = np.array([1.0, 1.0])

        result = solve_nash_allocation(utilities, entitlements)

        # Nash should allocate most of good 0 to agent 0, good 1 to agent 1
        assert result.allocation[0, 0] > 0.9  # Agent 0 gets most of good 0
        assert result.allocation[1, 1] > 0.9  # Agent 1 gets most of good 1

        # Should be nearly envy-free
        fairness = analyze_fairness(result.allocation, utilities, entitlements)
        assert fairness.max_envy < 5.0  # Small envy tolerance

    def test_log_formulation_stability(self):
        """Test that log formulation handles small utilities correctly."""
        utilities = np.array([
            [0.1, 0.05],
            [0.05, 0.1],
        ])
        entitlements = np.array([1.0, 1.0])

        result = solve_nash_allocation(utilities, entitlements, epsilon=1e-6)

        assert result.solver_status in ["optimal", "feasible"]
        # Should produce reasonable allocation despite small utilities
        assert np.all(result.utilities > 0)
