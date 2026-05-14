
# API Reference

## Core Functions

### `solve_maxmin_allocation`

```python
def solve_maxmin_allocation(
    utilities: npt.NDArray[np.float64],
    entitlements: npt.NDArray[np.float64],
    epsilon: float = 1e-6,
    time_limit_seconds: float = 300.0,
) -> AllocationResult
```

Solve the max-min fair allocation problem (egalitarian solution).

**Parameters:**
- `utilities`: Utility matrix of shape `(n_agents, n_goods)`. `utilities[i,j]` is agent i's utility for good j.
- `entitlements`: Entitlement weights of shape `(n_agents,)`. Must all be positive.
- `epsilon`: Small positive value to ensure min utility is strictly positive. Default: `1e-6`.
- `time_limit_seconds`: Maximum solver time in seconds. Default: `300`.

**Returns:**
- `AllocationResult` containing allocation, utilities, objective value, solver status, and solve time.

**Raises:**
- `ValueError`: If inputs are malformed.

**Example:**
```python
import numpy as np
from fair_division import solve_maxmin_allocation

utilities = np.array([[10, 5], [5, 10]])
entitlements = np.array([1.0, 1.0])
result = solve_maxmin_allocation(utilities, entitlements)
print(result.utilities)  # [7.5, 7.5] for this symmetric case
```

---

### `solve_nash_allocation`

```python
def solve_nash_allocation(
    utilities: npt.NDArray[np.float64],
    entitlements: npt.NDArray[np.float64],
    epsilon: float = 1e-6,
    time_limit_seconds: float = 300.0,
    solver_options: Optional[dict] = None,
) -> AllocationResult
```

Solve the Nash social welfare maximization problem.

**Parameters:**
- `utilities`: Utility matrix of shape `(n_agents, n_goods)`.
- `entitlements`: Entitlement weights of shape `(n_agents,)`. Must all be positive.
- `epsilon`: Lower bound on utilities to ensure log is defined. Default: `1e-6`.
- `time_limit_seconds`: Maximum solver time (not strictly enforced by SciPy). Default: `300`.
- `solver_options`: Optional dict of options to pass to `scipy.optimize.minimize`.

**Returns:**
- `AllocationResult` containing allocation, utilities, objective value, solver status, and solve time.

**Raises:**
- `ValueError`: If inputs are malformed.

**Example:**
```python
import numpy as np
from fair_division import solve_nash_allocation

utilities = np.array([[10, 5], [5, 10]])
entitlements = np.array([1.0, 1.0])
result = solve_nash_allocation(utilities, entitlements)
print(result.utilities)
```

---

### `analyze_fairness`

```python
def analyze_fairness(
    allocation: npt.NDArray[np.float64],
    utilities: npt.NDArray[np.float64],
    entitlements: npt.NDArray[np.float64],
    tolerance: float = 1e-6,
) -> FairnessReport
```

Comprehensive fairness analysis of an allocation.

**Parameters:**
- `allocation`: Allocation matrix of shape `(n_agents, n_goods)`. `allocation[i,j]` is the fraction of good j given to agent i.
- `utilities`: Utility matrix of shape `(n_agents, n_goods)`.
- `entitlements`: Entitlement weights of shape `(n_agents,)`.
- `tolerance`: Numerical tolerance for comparisons. Default: `1e-6`.

**Returns:**
- `FairnessReport` object containing:
  - Welfare metrics (utilities, total, Nash, min)
  - Pareto efficiency status
  - Envy analysis (matrix, max envy, envious pairs)
  - Proportionality analysis
  - Symmetry checks
  - Overall fairness summary

**Example:**
```python
from fair_division import solve_nash_allocation, analyze_fairness
import numpy as np

utilities = np.array([[10, 5], [5, 10]])
entitlements = np.array([1.0, 1.0])
result = solve_nash_allocation(utilities, entitlements)
report = analyze_fairness(result.allocation, utilities, entitlements)

print(report)
print(f"Envy-free: {report.is_envy_free}")
print(f"Max envy: {report.max_envy:.4f}")
```

---

## Data Models

### `AllocationResult`

Result of a fair division algorithm.

**Attributes:**
- `allocation`: Matrix `x[i,j]` representing the fraction of good j allocated to agent i. Shape: `(n_agents, n_goods)`.
- `utilities`: Array of total utilities achieved by each agent. Shape: `(n_agents,)`.
- `objective_value`: The value of the optimization objective.
- `solver_status`: String indicating solver status (`'optimal'`, `'feasible'`, `'infeasible'`).
- `solve_time`: Time in seconds to solve the optimization problem.
- `metadata`: Dict with additional solver-specific information.

**Example:**
```python
result = solve_maxmin_allocation(utilities, entitlements)
print(f"Status: {result.solver_status}")
print(f"Time: {result.solve_time:.4f}s")
print(f"Min utility: {result.utilities.min():.4f}")
```

---

### `FairnessReport`

Comprehensive fairness analysis of an allocation.

**Attributes:**

*Welfare Metrics:*
- `utilities`: Per-agent realized utilities. Shape: `(n_agents,)`.
- `total_utility`: Sum of all agent utilities.
- `nash_welfare`: Geometric mean of utilities (Nash social welfare).
- `min_utility`: Minimum utility (egalitarian welfare).

*Pareto Efficiency:*
- `is_pareto_efficient`: Boolean indicating if allocation is Pareto efficient (heuristic).
- `pareto_check_note`: Explanation of Pareto efficiency determination.

*Envy Analysis:*
- `envy_matrix`: Matrix where entry `[i,k]` is how much agent i envies agent k. Shape: `(n_agents, n_agents)`.
- `max_envy`: Maximum envy value across all agent pairs.
- `is_envy_free`: True if max envy ≈ 0.
- `envious_pairs`: List of `(i, k, envy_amount)` tuples.

*Proportionality:*
- `proportional_shares`: For each agent, their proportional share of total utility.
- `proportionality_gaps`: For each agent, `U_i - proportional_share[i]`.
- `is_proportional`: True if all agents get at least their proportional share.

*Symmetry:*
- `is_symmetric_instance`: True if all agents have identical utilities and entitlements.
- `is_symmetric_allocation`: True if symmetric agents receive equal utilities.

*Summary:*
- `fairness_summary`: Dict with high-level fairness metrics.

**Methods:**
- `__str__()`: Returns a human-readable fairness report.

**Example:**
```python
report = analyze_fairness(allocation, utilities, entitlements)
print(report)  # Prints formatted report

# Access specific metrics
if report.is_envy_free:
    print("Allocation is envy-free!")
else:
    print(f"Max envy: {report.max_envy:.4f}")
    for i, k, envy in report.envious_pairs[:3]:
        print(f"  Agent {i} envies agent {k} by {envy:.4f}")
```

---

## Utility Functions

### `validate_inputs`

```python
def validate_inputs(
    utilities: npt.NDArray[np.float64],
    entitlements: npt.NDArray[np.float64],
) -> Tuple[int, int]
```

Validate utility matrix and entitlements.

**Returns:** `(n_agents, n_goods)`

**Raises:** `ValueError` if inputs are invalid.

---

### `normalize_allocation`

```python
def normalize_allocation(
    allocation: npt.NDArray[np.float64],
    tolerance: float = 1e-9,
) -> npt.NDArray[np.float64]
```

Normalize allocation so each good is fully allocated (columns sum to 1).

---

### `generate_random_utilities`

```python
def generate_random_utilities(
    n_agents: int,
    n_goods: int,
    low: float = 0.0,
    high: float = 10.0,
    seed: int = None,
) -> npt.NDArray[np.float64]
```

Generate random utility matrix for testing.

---

### `generate_symmetric_utilities`

```python
def generate_symmetric_utilities(
    n_agents: int,
    utilities_per_agent: npt.NDArray[np.float64],
) -> npt.NDArray[np.float64]
```

Generate symmetric utility matrix where all agents have identical utilities.

---

### `compute_envy_matrix`

```python
def compute_envy_matrix(
    allocation: npt.NDArray[np.float64],
    utilities: npt.NDArray[np.float64],
) -> npt.NDArray[np.float64]
```

Compute the envy matrix for an allocation.

**Returns:** Envy matrix of shape `(n_agents, n_agents)` where entry `[i,k]` is `max(0, U_i(bundle_k) - U_i(bundle_i))`.

---

### `check_ef1`

```python
def check_ef1(
    allocation: npt.NDArray[np.float64],
    utilities: npt.NDArray[np.float64],
    tolerance: float = 1e-6,
) -> bool
```

Check if an allocation is EF1 (envy-free up to one good).

Mainly meaningful for discrete allocations.

**Returns:** `True` if allocation is EF1, `False` otherwise.

---

## Complete Example

```python
import numpy as np
from fair_division import (
    solve_maxmin_allocation,
    solve_nash_allocation,
    analyze_fairness,
)

# Define instance
utilities = np.array([
    [10.0, 5.0, 8.0],
    [6.0, 9.0, 7.0],
    [8.0, 7.0, 9.0],
])
entitlements = np.array([1.0, 1.0, 1.0])

# Solve with both algorithms
result_maxmin = solve_maxmin_allocation(utilities, entitlements)
result_nash = solve_nash_allocation(utilities, entitlements)

# Analyze fairness
fairness_maxmin = analyze_fairness(
    result_maxmin.allocation, utilities, entitlements
)
fairness_nash = analyze_fairness(
    result_nash.allocation, utilities, entitlements
)

# Compare
print("Max-Min:")
print(f"  Min utility: {result_maxmin.utilities.min():.4f}")
print(f"  Envy-free: {fairness_maxmin.is_envy_free}")

print("\nNash:")
print(f"  Nash welfare: {fairness_nash.nash_welfare:.4f}")
print(f"  Envy-free: {fairness_nash.is_envy_free}")

# Full reports
print("\n" + "="*80)
print(fairness_maxmin)
print("\n" + "="*80)
print(fairness_nash)
```

---

## Performance Tips

1. **Problem Size**: Both solvers handle up to ~100 agents and ~100 goods efficiently on modern hardware.

2. **Epsilon Tuning**: If you encounter numerical issues, try:
   - Increasing `epsilon` (e.g., `1e-5` or `1e-4`) for more stability
   - Decreasing `epsilon` (e.g., `1e-8`) for higher precision

3. **Solver Options (Nash)**:
   ```python
   result = solve_nash_allocation(
       utilities,
       entitlements,
       solver_options={'maxiter': 500, 'ftol': 1e-8}
   )
   ```

4. **Scaling Utilities**: If utilities have vastly different magnitudes, consider normalizing them first.

5. **Warm Start**: For repeated solves with similar instances, you can use the previous allocation as an initial guess (requires modifying the solver).

---

## Error Handling

All solvers validate inputs and raise `ValueError` for:
- Negative utilities
- Zero or negative entitlements
- Mismatched array dimensions
- Invalid epsilon values

Example:
```python
try:
    result = solve_nash_allocation(utilities, entitlements)
except ValueError as e:
    print(f"Invalid input: {e}")
```

---

## Type Hints

All functions are fully type-hinted for use with mypy and other type checkers:

```python
from typing import Optional
import numpy.typing as npt

def solve_nash_allocation(
    utilities: npt.NDArray[np.float64],
    entitlements: npt.NDArray[np.float64],
    epsilon: float = 1e-6,
    time_limit_seconds: float = 300.0,
    solver_options: Optional[dict] = None,
) -> AllocationResult:
    ...
```

---

## Testing

Run the test suite:

```bash
cd fair_division_lib
pytest tests/ -v
```

Run specific test modules:
```bash
pytest tests/test_nash.py -v
pytest tests/test_game_theoretic_properties.py -v
```

Run with coverage:
```bash
pytest tests/ --cov=fair_division --cov-report=html
```

---

## Examples

See the `examples/` directory for complete working examples:

- `basic_example.py`: Basic usage of both solvers
- `symmetric_instance.py`: Demonstrates symmetry axiom
- `weighted_entitlements.py`: Shows effect of entitlement weights

Run examples:
```bash
cd fair_division_lib
python -m examples.basic_example
python -m examples.symmetric_instance
python -m examples.weighted_entitlements
```
