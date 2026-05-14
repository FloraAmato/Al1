"""
Fair Division Library

A production-grade library for game-theoretic fair allocation of divisible goods.
"""

from .models import AllocationResult, FairnessReport
from .maxmin_solver import solve_maxmin_allocation
from .nash_solver import solve_nash_allocation
from .diagnostics import analyze_fairness

__version__ = "1.0.0"
__all__ = [
    "AllocationResult",
    "FairnessReport",
    "solve_maxmin_allocation",
    "solve_nash_allocation",
    "analyze_fairness",
]
