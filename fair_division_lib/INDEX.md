# Fair Division Library - Complete Index

## 🎯 Start Here

**New Users**: Start with [QUICKSTART.md](QUICKSTART.md) for a 5-minute tutorial.

**Researchers**: Read [SUMMARY.md](SUMMARY.md) for a complete overview, then [docs/theoretical_foundation.md](docs/theoretical_foundation.md).

**Developers**: Check [docs/api_reference.md](docs/api_reference.md) and the `examples/` directory.

---

## 📋 Complete File Index

### 📖 Documentation (Read in this order)

| File | Purpose | When to Read |
|------|---------|--------------|
| [README.md](README.md) | Overview & quick start | **Start here** |
| [QUICKSTART.md](QUICKSTART.md) | 5-minute tutorial | After README |
| [SUMMARY.md](SUMMARY.md) | Complete summary of theory & implementation | For comprehensive understanding |
| [docs/theoretical_foundation.md](docs/theoretical_foundation.md) | In-depth game-theoretic foundations | For deep theoretical understanding |
| [docs/api_reference.md](docs/api_reference.md) | Complete API documentation | When writing code |
| [MANIFEST.md](MANIFEST.md) | Package contents & statistics | For overview of what's included |

### 🐍 Source Code

| File | Contains | Key Functions/Classes |
|------|----------|----------------------|
| [src/fair_division/__init__.py](src/fair_division/__init__.py) | Package exports | - |
| [src/fair_division/models.py](src/fair_division/models.py) | Data structures | `AllocationResult`, `FairnessReport` |
| [src/fair_division/maxmin_solver.py](src/fair_division/maxmin_solver.py) | Max-Min solver | `solve_maxmin_allocation()` |
| [src/fair_division/nash_solver.py](src/fair_division/nash_solver.py) | Nash solver | `solve_nash_allocation()` |
| [src/fair_division/diagnostics.py](src/fair_division/diagnostics.py) | Fairness analysis | `analyze_fairness()`, `compute_envy_matrix()`, `check_ef1()` |
| [src/fair_division/utils.py](src/fair_division/utils.py) | Utilities | `validate_inputs()`, `normalize_allocation()`, `generate_random_utilities()` |

### 💡 Examples (Run with `python -m examples.<name>`)

| File | Demonstrates | Key Concepts |
|------|--------------|--------------|
| [examples/basic_example.py](examples/basic_example.py) | Basic usage of both solvers | Allocation, fairness analysis, comparison |
| [examples/symmetric_instance.py](examples/symmetric_instance.py) | Symmetry axiom | Symmetric agents get equal utilities |
| [examples/weighted_entitlements.py](examples/weighted_entitlements.py) | Effect of entitlements | Monotonicity w.r.t. entitlements |

### ✅ Tests (Run with `pytest tests/`)

| File | Tests | Coverage |
|------|-------|----------|
| [tests/test_maxmin.py](tests/test_maxmin.py) | Max-Min solver | Feasibility, symmetry, normalized utilities, Pareto efficiency |
| [tests/test_nash.py](tests/test_nash.py) | Nash solver | Feasibility, symmetry, Nash welfare objective, monotonicity |
| [tests/test_diagnostics.py](tests/test_diagnostics.py) | Fairness diagnostics | Envy, proportionality, symmetry detection, EF1 |
| [tests/test_game_theoretic_properties.py](tests/test_game_theoretic_properties.py) | Game-theoretic axioms | Symmetry, Pareto, monotonicity, stability (both solvers) |

### ⚙️ Configuration

| File | Purpose |
|------|---------|
| [setup.py](setup.py) | Package installation configuration |
| [requirements.txt](requirements.txt) | Python dependencies (numpy, scipy, ortools, pydantic) |

---

## 🔍 Quick Reference

### Common Tasks

| Task | Location |
|------|----------|
| **Install the library** | See [README.md](README.md) or [QUICKSTART.md](QUICKSTART.md) |
| **Run basic example** | `python -m examples.basic_example` |
| **Understand theory** | [docs/theoretical_foundation.md](docs/theoretical_foundation.md) |
| **Look up API** | [docs/api_reference.md](docs/api_reference.md) |
| **Run tests** | `pytest tests/ -v` |
| **Check what's included** | [MANIFEST.md](MANIFEST.md) |

### Key Functions

| Function | Module | Purpose |
|----------|--------|---------|
| `solve_maxmin_allocation()` | `maxmin_solver` | Compute max-min fair allocation |
| `solve_nash_allocation()` | `nash_solver` | Compute Nash social welfare allocation |
| `analyze_fairness()` | `diagnostics` | Evaluate fairness of an allocation |
| `compute_envy_matrix()` | `diagnostics` | Compute envy between all agent pairs |
| `check_ef1()` | `diagnostics` | Check if allocation is EF1 |

### Key Classes

| Class | Module | Purpose |
|-------|--------|---------|
| `AllocationResult` | `models` | Result of a fair division solver |
| `FairnessReport` | `models` | Comprehensive fairness analysis |

---

## 📊 Theory Quick Reference

### Max-Min Fair Allocation

- **Objective**: Maximize `min_i { U_i / w_i }`
- **Concept**: Egalitarian solution (help worst-off agent)
- **Properties**: Pareto efficient, symmetric, monotonic
- **Not Guaranteed**: Envy-freeness
- **Use When**: Prioritize equity

### Nash Social Welfare

- **Objective**: Maximize `sum_i w_i * log(U_i)` (log formulation)
- **Concept**: Nash bargaining solution
- **Properties**: Pareto efficient, symmetric, IIA, monotonic
- **Not Guaranteed**: Envy-freeness
- **Use When**: Balance efficiency and fairness

### Fairness Diagnostics

- **Pareto Efficiency**: No wasted resources
- **Envy-Freeness**: No agent prefers another's bundle
- **Proportionality**: Everyone gets their fair share
- **Symmetry**: Identical agents get equal utilities

---

## 🎓 Learning Path

### Beginner

1. Read [README.md](README.md)
2. Follow [QUICKSTART.md](QUICKSTART.md) tutorial
3. Run `python -m examples.basic_example`
4. Modify the example with your own data

### Intermediate

1. Read [SUMMARY.md](SUMMARY.md) for complete overview
2. Study [examples/symmetric_instance.py](examples/symmetric_instance.py)
3. Study [examples/weighted_entitlements.py](examples/weighted_entitlements.py)
4. Run tests: `pytest tests/ -v`
5. Read docstrings in source code

### Advanced

1. Read [docs/theoretical_foundation.md](docs/theoretical_foundation.md)
2. Study [src/fair_division/maxmin_solver.py](src/fair_division/maxmin_solver.py)
3. Study [src/fair_division/nash_solver.py](src/fair_division/nash_solver.py)
4. Study [src/fair_division/diagnostics.py](src/fair_division/diagnostics.py)
5. Review [tests/test_game_theoretic_properties.py](tests/test_game_theoretic_properties.py)
6. Experiment with custom instances

### Researcher

1. Read all documentation files
2. Study the complete source code
3. Review all test cases
4. Read the references in [docs/theoretical_foundation.md](docs/theoretical_foundation.md)
5. Verify game-theoretic properties experimentally
6. Compare with other fair division algorithms

---

## 🚀 Usage Patterns

### Pattern 1: Quick Allocation

```python
from fair_division import solve_nash_allocation
import numpy as np

utilities = np.array([[10, 5], [5, 10]])
entitlements = np.array([1.0, 1.0])
result = solve_nash_allocation(utilities, entitlements)
print(result.utilities)
```

### Pattern 2: Allocation + Fairness Analysis

```python
from fair_division import solve_nash_allocation, analyze_fairness
import numpy as np

utilities = np.array([[10, 5], [5, 10]])
entitlements = np.array([1.0, 1.0])

result = solve_nash_allocation(utilities, entitlements)
report = analyze_fairness(result.allocation, utilities, entitlements)

print(f"Envy-free: {report.is_envy_free}")
print(f"Pareto efficient: {report.is_pareto_efficient}")
print(report)  # Full report
```

### Pattern 3: Compare Algorithms

```python
from fair_division import solve_maxmin_allocation, solve_nash_allocation, analyze_fairness
import numpy as np

utilities = np.array([[10, 5, 8], [6, 9, 7]])
entitlements = np.array([1.0, 1.0])

# Solve with both
result_mm = solve_maxmin_allocation(utilities, entitlements)
result_nash = solve_nash_allocation(utilities, entitlements)

# Compare
print("Max-Min utilities:", result_mm.utilities)
print("Nash utilities:", result_nash.utilities)

# Analyze both
report_mm = analyze_fairness(result_mm.allocation, utilities, entitlements)
report_nash = analyze_fairness(result_nash.allocation, utilities, entitlements)

print(f"\nMax-Min: Envy-free={report_mm.is_envy_free}, Max envy={report_mm.max_envy:.4f}")
print(f"Nash: Envy-free={report_nash.is_envy_free}, Max envy={report_nash.max_envy:.4f}")
```

---

## 🔬 Research Applications

This library is suitable for research in:

1. **Fair Division Theory**: Testing axioms, comparing solution concepts
2. **Algorithmic Game Theory**: Analyzing computational properties
3. **Mechanism Design**: Designing fair allocation mechanisms
4. **Resource Allocation**: Healthcare, disaster relief, network bandwidth
5. **Computational Social Choice**: Voting, committee selection
6. **Economics**: Surplus division, tax allocation

---

## 📞 Support & Contributions

- **Bug Reports**: Check inputs are valid, review error messages
- **Feature Requests**: Consider forking and extending
- **Questions**: Review documentation, especially [docs/theoretical_foundation.md](docs/theoretical_foundation.md)
- **Improvements**: Tests and examples show how to extend functionality

---

## 📝 License

MIT License - See project files for details

---

**Version**: 1.0.0
**Last Updated**: November 2025
**Total Files**: 29
**Total Tests**: 62
**Lines of Code**: ~3,500
**Documentation Pages**: 6
