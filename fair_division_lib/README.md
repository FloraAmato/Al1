# Fair Division Library

A production-grade Python library for fair allocation of divisible goods using game-theoretic principles.

## Overview

This library implements two fundamental fair division algorithms:

1. **Max-Min Fair Allocation** (Egalitarian Solution)
   - Maximizes the minimum utility across all agents
   - Approximates the egalitarian bargaining solution
   - Guarantees Pareto efficiency under convexity

2. **Nash Social Welfare Maximization**
   - Maximizes the weighted geometric mean of utilities
   - Implements the Nash bargaining solution
   - Uses numerically stable log formulation

## Key Features

- **Theoretically Grounded**: All algorithms are firmly rooted in cooperative game theory
- **Fairness Diagnostics**: Comprehensive analysis of envy, proportionality, and Pareto efficiency
- **Production-Ready**: Type hints, extensive tests, clear documentation
- **Numerical Stability**: Log formulations and careful handling of edge cases

## Installation

```bash
pip install -r requirements.txt
```

## Quick Start

```python
from fair_division import solve_nash_allocation, analyze_fairness
import numpy as np

# Define utilities: 3 agents, 4 goods
utilities = np.array([
    [10, 5, 8, 3],   # Agent 0's utilities
    [7, 9, 4, 6],    # Agent 1's utilities
    [5, 6, 10, 8]    # Agent 2's utilities
])

# Equal entitlements
entitlements = np.array([1.0, 1.0, 1.0])

# Solve using Nash social welfare
result = solve_nash_allocation(utilities, entitlements)

# Analyze fairness
report = analyze_fairness(result.allocation, utilities, entitlements)
print(report)
```

## Documentation

See `docs/` for:
- Theoretical foundations
- API reference
- Game-theoretic properties
- Limitations and caveats

## License

MIT
