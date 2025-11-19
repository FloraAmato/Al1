# Quick Start Guide

## Installation

```bash
# Extract the zip file
unzip fair_division_library.zip
cd fair_division_lib

# Install dependencies
pip install -r requirements.txt

# Install the library
pip install -e .
```

## 5-Minute Tutorial

### Example 1: Basic Fair Division

```python
import numpy as np
from fair_division import solve_nash_allocation, solve_maxmin_allocation, analyze_fairness

# Two agents, two goods
# Agent 0 prefers good 0, Agent 1 prefers good 1
utilities = np.array([
    [10.0, 5.0],  # Agent 0
    [5.0, 10.0],  # Agent 1
])

# Equal entitlements
entitlements = np.array([1.0, 1.0])

# Solve with Nash
result_nash = solve_nash_allocation(utilities, entitlements)
print("Nash allocation:")
print(result_nash.allocation)
print("Utilities:", result_nash.utilities)

# Solve with Max-Min
result_maxmin = solve_maxmin_allocation(utilities, entitlements)
print("\nMax-Min allocation:")
print(result_maxmin.allocation)
print("Utilities:", result_maxmin.utilities)

# Analyze fairness
report = analyze_fairness(result_nash.allocation, utilities, entitlements)
print("\nFairness Report:")
print(report)
```

### Example 2: Weighted Entitlements

```python
# Agent 0 has 2x the entitlement
entitlements = np.array([2.0, 1.0])

result = solve_nash_allocation(utilities, entitlements)
print("Utilities:", result.utilities)
# Agent 0 should get more utility due to higher entitlement
```

### Example 3: Symmetric Instance

```python
# Both agents have identical preferences
utilities = np.array([
    [10.0, 5.0, 8.0],
    [10.0, 5.0, 8.0],
])
entitlements = np.array([1.0, 1.0])

result = solve_nash_allocation(utilities, entitlements)
print("Utilities:", result.utilities)
# Should be equal due to symmetry axiom
```

## Running Examples

```bash
# Run the provided examples
python -m examples.basic_example
python -m examples.symmetric_instance
python -m examples.weighted_entitlements
```

## Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific tests
pytest tests/test_nash.py -v
pytest tests/test_game_theoretic_properties.py -v

# Run with coverage
pytest tests/ --cov=fair_division --cov-report=html
```

## Understanding the Output

### AllocationResult
- `allocation`: Matrix where `allocation[i,j]` is the fraction of good j given to agent i
- `utilities`: Total utility for each agent
- `objective_value`: The optimization objective (log Nash welfare or min utility)
- `solver_status`: 'optimal' or 'feasible'

### FairnessReport
- `is_envy_free`: Are all agents satisfied with their bundle?
- `max_envy`: Maximum envy between any two agents
- `is_pareto_efficient`: Could we make someone better off without hurting anyone?
- `is_proportional`: Does each agent get their fair share?

## Next Steps

1. Read `SUMMARY.md` for a complete overview
2. Read `docs/theoretical_foundation.md` for deep theoretical understanding
3. Read `docs/api_reference.md` for API details
4. Explore the examples in `examples/`
5. Review the tests in `tests/` for more usage patterns

## Common Questions

**Q: Which algorithm should I use?**
- Use **Nash** for balanced efficiency and fairness
- Use **Max-Min** to prioritize the worst-off agent

**Q: What if I get numerical errors?**
- Try increasing `epsilon` parameter (e.g., `epsilon=1e-4`)
- Check that utilities are non-negative
- Normalize utilities if they span many orders of magnitude

**Q: How do I interpret the fairness report?**
- `is_envy_free=True`: No agent wants another's bundle
- `is_pareto_efficient=True`: No wasted resources
- `is_proportional=True`: Everyone gets their fair share

**Q: Can I use this for indivisible goods?**
- Not directly. Both algorithms assume divisibility.
- For indivisible goods, use the allocation as a guide for randomized assignment

## Getting Help

- Check the examples in `examples/`
- Read the full documentation in `docs/`
- Review test cases in `tests/`
- Check function docstrings (e.g., `help(solve_nash_allocation)`)
