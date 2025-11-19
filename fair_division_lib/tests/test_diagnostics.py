"""
Tests for fairness diagnostics module.
"""

import pytest
import numpy as np
from fair_division import analyze_fairness
from fair_division.diagnostics import compute_envy_matrix, check_ef1


class TestFairnessDiagnostics:
    """Test suite for fairness diagnostics."""

    def test_envy_free_allocation(self):
        """Test diagnosis of an envy-free allocation."""
        # Each agent gets their preferred good entirely
        allocation = np.array([
            [1.0, 0.0],
            [0.0, 1.0],
        ])
        utilities = np.array([
            [10.0, 5.0],
            [5.0, 10.0],
        ])
        entitlements = np.array([1.0, 1.0])

        report = analyze_fairness(allocation, utilities, entitlements)

        assert report.is_envy_free
        assert report.max_envy < 1e-6
        assert len(report.envious_pairs) == 0

    def test_envious_allocation(self):
        """Test diagnosis of an allocation with envy."""
        # Agent 0 gets everything
        allocation = np.array([
            [1.0, 1.0],
            [0.0, 0.0],
        ])
        utilities = np.array([
            [10.0, 5.0],
            [5.0, 10.0],
        ])
        entitlements = np.array([1.0, 1.0])

        report = analyze_fairness(allocation, utilities, entitlements)

        assert not report.is_envy_free
        assert report.max_envy > 0
        # Agent 1 should envy agent 0
        assert len(report.envious_pairs) > 0
        assert report.envious_pairs[0][0] == 1  # Agent 1 envies

    def test_proportionality_check(self):
        """Test proportionality diagnosis."""
        # Equal split
        allocation = np.array([
            [0.5, 0.5],
            [0.5, 0.5],
        ])
        utilities = np.array([
            [10.0, 10.0],
            [10.0, 10.0],
        ])
        entitlements = np.array([1.0, 1.0])

        report = analyze_fairness(allocation, utilities, entitlements)

        # Each agent gets utility 10.0, proportional share is 10.0
        assert report.is_proportional
        assert np.all(np.abs(report.proportionality_gaps) < 1e-6)

    def test_non_proportional_allocation(self):
        """Test diagnosis of non-proportional allocation."""
        # Agent 0 gets very little
        allocation = np.array([
            [0.1, 0.1],
            [0.9, 0.9],
        ])
        utilities = np.array([
            [10.0, 10.0],
            [10.0, 10.0],
        ])
        entitlements = np.array([1.0, 1.0])

        report = analyze_fairness(allocation, utilities, entitlements)

        # Agent 0 gets 2.0, should get 11.0 (half of 22.0)
        assert not report.is_proportional
        assert report.proportionality_gaps[0] < 0  # Negative gap for agent 0

    def test_symmetric_instance_detection(self):
        """Test detection of symmetric instances."""
        allocation = np.array([
            [0.5, 0.5],
            [0.5, 0.5],
        ])
        # Symmetric utilities
        utilities = np.array([
            [10.0, 5.0],
            [10.0, 5.0],
        ])
        entitlements = np.array([1.0, 1.0])

        report = analyze_fairness(allocation, utilities, entitlements)

        assert report.is_symmetric_instance
        assert report.is_symmetric_allocation

    def test_asymmetric_instance(self):
        """Test detection of asymmetric instances."""
        allocation = np.array([
            [0.5, 0.5],
            [0.5, 0.5],
        ])
        # Different utilities
        utilities = np.array([
            [10.0, 5.0],
            [5.0, 10.0],
        ])
        entitlements = np.array([1.0, 1.0])

        report = analyze_fairness(allocation, utilities, entitlements)

        assert not report.is_symmetric_instance

    def test_envy_matrix_computation(self):
        """Test direct envy matrix computation."""
        allocation = np.array([
            [1.0, 0.0],
            [0.0, 1.0],
        ])
        utilities = np.array([
            [10.0, 8.0],
            [8.0, 10.0],
        ])

        envy_matrix = compute_envy_matrix(allocation, utilities)

        # Agent 0 gets good 0 (utility 10), might envy agent 1's good 1 (utility 8 to agent 0)
        # No envy since 10 >= 8
        assert envy_matrix[0, 1] == 0

        # Agent 1 gets good 1 (utility 10), might envy agent 0's good 0 (utility 8 to agent 1)
        # No envy since 10 >= 8
        assert envy_matrix[1, 0] == 0

    def test_ef1_check_discrete(self):
        """Test EF1 check for discrete allocations."""
        # Discrete allocation: agent 0 gets goods 0,1; agent 1 gets good 2
        allocation = np.array([
            [1.0, 1.0, 0.0],
            [0.0, 0.0, 1.0],
        ])
        utilities = np.array([
            [5.0, 3.0, 10.0],
            [5.0, 3.0, 10.0],
        ])

        # Agent 1 envies agent 0 (gets 10 vs agent 0's 8)
        # But if we remove good 0 (value 5) from agent 0, agent 0 has 3, agent 1 has 10
        # Still envy. Remove good 1 (value 3), agent 0 has 5, agent 1 has 10.
        # Still envy. So this is NOT EF1.

        is_ef1 = check_ef1(allocation, utilities)
        assert not is_ef1

    def test_welfare_metrics(self):
        """Test computation of welfare metrics."""
        allocation = np.array([
            [0.6, 0.4],
            [0.4, 0.6],
        ])
        utilities = np.array([
            [10.0, 5.0],
            [5.0, 10.0],
        ])
        entitlements = np.array([1.0, 1.0])

        report = analyze_fairness(allocation, utilities, entitlements)

        # Check welfare metrics
        assert report.total_utility == report.utilities.sum()
        assert report.min_utility == report.utilities.min()
        assert report.nash_welfare > 0

    def test_fairness_report_string(self):
        """Test that fairness report can be printed."""
        allocation = np.array([
            [0.5, 0.5],
            [0.5, 0.5],
        ])
        utilities = np.array([
            [10.0, 5.0],
            [5.0, 10.0],
        ])
        entitlements = np.array([1.0, 1.0])

        report = analyze_fairness(allocation, utilities, entitlements)

        # Should not raise an error
        report_str = str(report)
        assert "FAIRNESS ANALYSIS REPORT" in report_str
        assert "WELFARE METRICS" in report_str
