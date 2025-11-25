"""
Test game-theory algorithms.
"""
import pytest
from app.algorithms import MaxMinSolver, NashSolver


def test_maxmin_solver():
    """Test max-min fairness solver."""
    agents = [1, 2]
    goods = [1, 2]

    # Agent 1 prefers good 1, agent 2 prefers good 2
    utilities = {
        (1, 1): 10.0,
        (1, 2): 5.0,
        (2, 1): 5.0,
        (2, 2): 10.0,
    }

    entitlements = {1: 0.5, 2: 0.5}
    good_values = {1: 100.0, 2: 100.0}
    budget = 250.0

    solver = MaxMinSolver(
        agents=agents,
        goods=goods,
        utilities=utilities,
        entitlements=entitlements,
        good_values=good_values,
        budget=budget,
    )

    allocations, objective_value = solver.solve()

    assert objective_value > 0
    assert len(allocations) > 0

    # Check that allocations respect constraints
    for (agent_id, good_id), amount in allocations.items():
        assert amount >= 0
        assert amount <= 1


def test_nash_solver():
    """Test Nash social welfare solver."""
    agents = [1, 2]
    goods = [1, 2]

    utilities = {
        (1, 1): 10.0,
        (1, 2): 5.0,
        (2, 1): 5.0,
        (2, 2): 10.0,
    }

    entitlements = {1: 0.5, 2: 0.5}
    good_values = {1: 100.0, 2: 100.0}
    budget = 250.0

    solver = NashSolver(
        agents=agents,
        goods=goods,
        utilities=utilities,
        entitlements=entitlements,
        good_values=good_values,
        budget=budget,
    )

    allocations, objective_value = solver.solve()

    assert objective_value > 0
    assert len(allocations) > 0

    for (agent_id, good_id), amount in allocations.items():
        assert amount >= 0
        assert amount <= 1
