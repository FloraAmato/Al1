# Theoretical Foundation

## 1. Introduction

This library implements two fundamental approaches to fair division of divisible goods:

1. **Max-Min Fair Allocation** (Egalitarian Solution)
2. **Nash Social Welfare Maximization** (Nash Bargaining Solution)

Both algorithms are firmly grounded in cooperative game theory and fair division theory. This document provides a comprehensive theoretical foundation for understanding what these algorithms compute, which fairness and efficiency properties they satisfy, and their limitations.

---

## 2. Problem Setting

### 2.1 Fair Division Model

We consider the following setting:

- **Agents**: $n$ agents indexed by $i \in \{1, ..., n\}$
- **Goods**: $m$ divisible goods indexed by $j \in \{1, ..., m\}$
- **Utilities**: Utility matrix $u \in \mathbb{R}^{n \times m}$ where $u_{ij} \geq 0$ is agent $i$'s utility for receiving one full unit of good $j$
- **Allocations**: Allocation matrix $x \in [0,1]^{n \times m}$ where $x_{ij}$ is the fraction of good $j$ allocated to agent $i$
- **Entitlements**: Weight vector $w \in \mathbb{R}^n_{++}$ where $w_i > 0$ is agent $i$'s entitlement/claim

### 2.2 Utility Model

We assume:
- **Additivity**: Agent $i$'s total utility is $U_i = \sum_{j=1}^m u_{ij} x_{ij}$
- **Non-negativity**: $u_{ij} \geq 0$ for all $i, j$
- **Divisibility**: Goods can be divided arbitrarily (not discrete/indivisible)

### 2.3 Feasibility Constraints

An allocation is **feasible** if:
1. **Non-negativity**: $x_{ij} \geq 0$ for all $i, j$
2. **Full allocation**: $\sum_{i=1}^n x_{ij} = 1$ for all $j$ (each good is fully distributed)

---

## 3. Max-Min Fair Allocation (Egalitarian Solution)

### 3.1 Concept and Motivation

The max-min solution seeks to maximize the welfare of the **worst-off agent**. This corresponds to the **egalitarian bargaining solution** in cooperative game theory.

The philosophy is: *"A society is only as strong as its weakest member."*

### 3.2 Mathematical Formulation

**Objective**: Maximize $\min_{i=1,...,n} \frac{U_i}{w_i}$

**Subject to**:
- $U_i = \sum_{j=1}^m u_{ij} x_{ij}$ for all $i$
- $\sum_{i=1}^n x_{ij} = 1$ for all $j$
- $x_{ij} \geq 0$ for all $i, j$

We normalize by entitlements $w_i$ so that an agent with entitlement 2 "deserves" twice the utility.

**Equivalent LP Formulation**:
```
Maximize t
Subject to:
    ∑_j u_ij x_ij ≥ t · w_i   for all i
    ∑_i x_ij = 1               for all j
    x_ij ≥ 0                   for all i,j
    t ≥ ε                      (numerical stability)
```

### 3.3 Game-Theoretic Properties

Under standard assumptions (non-negative utilities, positive entitlements, convex feasible set):

#### ✓ **Pareto Efficiency**
The max-min solution is **Pareto efficient**: you cannot increase any agent's utility without decreasing the minimum utility.

**Proof sketch**: If we could Pareto-improve the allocation, we could increase the minimum utility, contradicting optimality.

#### ✓ **Symmetry**
If agents $i$ and $k$ have identical utility functions ($u_i = u_k$) and identical entitlements ($w_i = w_k$), they receive allocations yielding **equal utilities**.

**Rationale**: There is no reason to treat identical agents differently; any asymmetric solution could be "mirrored" to improve the minimum.

#### ✓ **Monotonicity w.r.t. Entitlements**
If we increase agent $i$'s entitlement $w_i$, their utility $U_i$ generally increases (or at least does not decrease significantly).

**Caveat**: The relationship depends on the constraint set. In pathological cases, redistribution may occur.

#### ✓ **Scale Invariance**
Scaling all utilities by a constant $c > 0$ does not change the allocation, only the utility values (which scale proportionally).

#### ✗ **Envy-Freeness**
Max-min does **NOT** guarantee envy-freeness. An agent may prefer another's bundle even if normalized utilities are equal.

**Example**: Agent 0 has $U_0/w_0 = 10$, agent 1 has $U_1/w_1 = 10$. But agent 0 might value agent 1's bundle at 15 under their own utility function.

#### ~ **Proportionality**
Max-min provides a **weighted proportionality** guarantee: each agent gets utility proportional to their entitlement, in the sense that normalized utilities are equalized.

### 3.4 Limitations and Caveats

1. **Zero Utilities**: If an agent has $u_{ij} = 0$ for all goods $j$, their utility is always zero, making max-min trivial. We add $\epsilon$ constraints to ensure $t > 0$.

2. **Multiple Optima**: The basic max-min may have multiple optimal solutions with the same minimum utility. A **lexicographic max-min** (maximize min, then second-min, etc.) is theoretically superior but computationally harder.

3. **Non-Envy**: Max-min focuses on equality of normalized utilities, not absence of envy.

4. **Discrete Goods**: For indivisible goods, the problem is NP-hard. This solver assumes divisibility.

---

## 4. Nash Social Welfare Maximization (Nash Bargaining Solution)

### 4.1 Concept and Motivation

The Nash social welfare (NSW) maximizer seeks an allocation that maximizes the **weighted geometric mean** of utilities:

$$\text{NSW} = \prod_{i=1}^n U_i^{w_i}$$

This corresponds to the **Nash bargaining solution** from cooperative game theory, which uniquely satisfies a set of desirable axioms (Pareto efficiency, symmetry, independence of irrelevant alternatives, invariance to utility rescaling).

The philosophy is: *"Balance efficiency and fairness by multiplicatively aggregating utilities."*

### 4.2 Mathematical Formulation (Log Form)

To avoid numerical overflow/underflow, we maximize the **log of the Nash product**:

**Objective**: Maximize $\sum_{i=1}^n w_i \log(U_i)$

**Subject to**:
- $U_i = \sum_{j=1}^m u_{ij} x_{ij}$ for all $i$
- $\sum_{i=1}^n x_{ij} = 1$ for all $j$
- $x_{ij} \geq 0$ for all $i, j$
- $U_i \geq \epsilon$ for all $i$ (strict positivity for log)

**Why Log Formulation?**
- **Numerical Stability**: Products can easily overflow/underflow; sums of logs are stable
- **Convexity**: The log objective is concave, making the problem a convex optimization
- **Equivalence**: Since $\log$ is monotone increasing, $\max \sum w_i \log U_i \equiv \max \prod U_i^{w_i}$

### 4.3 Game-Theoretic Properties

The Nash bargaining solution satisfies the **Nash axioms**:

#### ✓ **Pareto Efficiency**
The Nash solution is **always Pareto efficient**. This is a fundamental theorem.

**Proof sketch**: At optimum, the gradient of the Nash product is perpendicular to the Pareto frontier. Any Pareto improvement would increase the product, contradicting optimality.

#### ✓ **Symmetry**
If agents $i$ and $k$ have identical utilities and entitlements, they receive **equal utilities**.

#### ✓ **Scale Invariance** (with caveats)
The Nash bargaining solution is invariant to **positive affine transformations** of utilities *when there is a proper disagreement point*. In our model with zero disagreement point:
- Scaling *all* agents' utilities by the same constant does not change the allocation
- Scaling *one* agent's utilities changes the allocation (increases their share)

#### ✓ **Independence of Irrelevant Alternatives (IIA)**
If we shrink the feasible set and the Nash solution remains feasible, it remains the Nash solution.

#### ✓ **Monotonicity w.r.t. Entitlements**
Increasing agent $i$'s weight $w_i$ increases their utility $U_i$ (tilts the solution in their favor).

**Intuition**: Higher $w_i$ means agent $i$'s utility enters the objective with a higher exponent, so the optimizer allocates more to them.

#### ✗ **Envy-Freeness**
Nash welfare does **NOT** guarantee envy-freeness in general. It focuses on efficiency and proportional fairness (w.r.t. weights), but envy can still occur.

#### ~ **Proportionality**
The Nash solution tends to allocate utilities *roughly* in proportion to entitlements, but this is not a strict guarantee for all utility functions. It is a **tendency**, not a theorem.

### 4.4 Why Maximize Nash Welfare?

1. **Axiomatic Justification**: Nash proved that NSW is the *unique* solution satisfying Pareto efficiency, symmetry, scale invariance, and IIA.

2. **Balances Efficiency and Equity**:
   - Pure utilitarian welfare ($\sum U_i$) can be very unequal
   - Pure max-min welfare ($\min U_i$) can be very inefficient
   - Nash welfare is a **compromise**: it's a concave aggregation that rewards both total welfare and balance

3. **Proportional Fairness**: In network resource allocation and economics, NSW is known as the **proportionally fair** allocation.

### 4.5 Limitations and Caveats

1. **Zero Utilities**: If any $U_i = 0$, the Nash product is zero. We enforce $U_i \geq \epsilon$ to ensure logarithm is defined. Larger $\epsilon$ increases stability but may distort the solution.

2. **Envy**: Nash welfare does not guarantee envy-freeness.

3. **Computational Complexity**: The log-NSW objective is smooth and concave, so we can use nonlinear solvers (e.g., SciPy SLSQP). This is efficient for moderate-sized problems.

4. **Discrete Goods**: For indivisible goods, maximizing Nash welfare is **NP-hard**. This solver assumes divisibility.

---

## 5. Fairness and Efficiency Criteria

### 5.1 Pareto Efficiency

**Definition**: An allocation is **Pareto efficient** if no other allocation makes at least one agent strictly better off without making any agent worse off.

**Status**:
- **Max-Min**: Pareto efficient (proven theoretically, checked heuristically in code)
- **Nash**: Pareto efficient (guaranteed by Nash bargaining theorem)

### 5.2 Envy-Freeness (EF)

**Definition**: An allocation is **envy-free** if no agent $i$ prefers another agent $k$'s bundle to their own:
$$U_i(\text{bundle}_i) \geq U_i(\text{bundle}_k) \quad \forall i, k$$

**Status**:
- **Max-Min**: NOT guaranteed
- **Nash**: NOT guaranteed

**Measurement**: We compute an **envy matrix** where entry $[i,k] = \max(0, U_i(\text{bundle}_k) - U_i(\text{bundle}_i))$ measures how much agent $i$ envies agent $k$.

### 5.3 Proportionality

**Definition**: Agent $i$ receives at least their proportional share of the total welfare:
$$U_i \geq \frac{w_i}{\sum_k w_k} \cdot \sum_k U_k$$

**Status**:
- **Max-Min**: Provides a *normalized* proportionality (equalizes $U_i / w_i$)
- **Nash**: Tends toward proportionality but no strict guarantee

### 5.4 Envy-Freeness up to One Good (EF1)

**Definition** (for discrete allocations): An allocation is **EF1** if for any envious pair $(i, k)$, removing one good from $k$'s bundle eliminates $i$'s envy.

**Status**: Mainly relevant for discrete goods; for divisible goods we focus on EF.

---

## 6. Comparison of Algorithms

| Property | Max-Min | Nash | Notes |
|----------|---------|------|-------|
| **Pareto Efficiency** | ✓ Yes | ✓ Yes | Both guaranteed |
| **Symmetry** | ✓ Yes | ✓ Yes | Both satisfy |
| **Envy-Freeness** | ✗ No | ✗ No | Neither guarantees EF |
| **Proportionality** | ~ Normalized | ~ Tendency | Different interpretations |
| **Monotonicity (entitlements)** | ✓ Yes | ✓ Yes | Both satisfy |
| **Focus** | Worst-off agent | Geometric mean | Philosophical difference |
| **Objective** | $\max \min U_i/w_i$ | $\max \prod U_i^{w_i}$ | - |
| **Complexity** | Linear Program | Convex NLP | Both efficient |

**When to Use Which?**
- **Max-Min**: When you prioritize **equity** and want to maximize the welfare of the worst-off agent. Suitable for resource allocation in critical systems (healthcare, disaster relief).
- **Nash**: When you want to **balance efficiency and fairness**. Suitable for economic resource allocation, network bandwidth sharing, etc.

---

## 7. Implementation Details

### 7.1 Max-Min Solver

- **Formulation**: Linear Program (LP) with auxiliary variable $t = \min_i U_i / w_i$
- **Solver**: OR-Tools GLOP (linear programming solver)
- **Complexity**: Polynomial time; very fast even for large instances
- **Numerical Stability**: LPs are numerically stable; we add $t \geq \epsilon$ to avoid degeneracy

### 7.2 Nash Solver

- **Formulation**: Nonlinear convex optimization with log objective
- **Solver**: SciPy `minimize` with SLSQP method (Sequential Least Squares Programming)
- **Complexity**: Polynomial time for moderate-sized problems; gradient-based
- **Numerical Stability**: Log formulation avoids overflow/underflow; $U_i \geq \epsilon$ ensures log is defined

### 7.3 Epsilon Parameter

Both solvers use an **epsilon parameter** ($\epsilon$, default $10^{-6}$) to ensure strict positivity:
- **Max-Min**: Enforces $t \geq \epsilon$
- **Nash**: Enforces $U_i \geq \epsilon$

**Trade-off**:
- **Smaller $\epsilon$**: Closer to true optimum, but may cause numerical issues if utilities can be very small
- **Larger $\epsilon$**: More stable, but may distort the solution slightly

For most applications, $\epsilon = 10^{-6}$ is appropriate.

---

## 8. Fairness Diagnostics

The library provides a comprehensive **fairness diagnostics module** that evaluates allocations against multiple criteria:

### 8.1 Metrics Computed

1. **Welfare Metrics**:
   - Total utility: $\sum_i U_i$
   - Min utility: $\min_i U_i$
   - Nash welfare: $\prod_i U_i^{w_i}$

2. **Pareto Efficiency**: Heuristic check for obvious inefficiencies

3. **Envy Analysis**:
   - Envy matrix: $E_{ik} = \max(0, U_i(\text{bundle}_k) - U_i(\text{bundle}_i))$
   - Max envy: $\max_{i,k} E_{ik}$
   - Envious pairs: list of $(i, k, \text{envy})$ tuples

4. **Proportionality**:
   - Proportional shares: $\frac{w_i}{\sum_k w_k} \cdot \sum_k U_k$
   - Gaps: $U_i - \text{proportional share}_i$

5. **Symmetry**:
   - Detects symmetric instances
   - Checks if symmetric agents receive symmetric allocations

### 8.2 Fairness Report

The `analyze_fairness()` function returns a `FairnessReport` object with all metrics and a human-readable summary.

---

## 9. Limitations and Future Work

### 9.1 Current Limitations

1. **Divisible Goods Only**: Both solvers assume goods are perfectly divisible. For indivisible goods, the problem is NP-hard.

2. **Additive Utilities**: We assume utilities are additive across goods. Complementarities (e.g., "I value coffee and milk together more than separately") are not supported.

3. **No Strategic Behavior**: We assume agents truthfully report utilities. In practice, agents may misreport to manipulate the allocation (mechanism design issue).

4. **Heuristic Pareto Check**: Full Pareto efficiency verification requires solving an optimization problem; we use a heuristic check.

5. **No Fairness Constraints**: We do not enforce envy-freeness or other fairness constraints; we only measure them ex-post.

### 9.2 Future Enhancements

1. **Lexicographic Max-Min**: Implement a multi-stage max-min to refine tie-breaking.

2. **Indivisible Goods**: Add approximation algorithms for discrete goods (e.g., greedy EF1, round-robin).

3. **Strategic Robustness**: Analyze incentive compatibility and design truthful mechanisms.

4. **Additional Objectives**: Implement other social welfare functions (utilitarian, Kalai-Smorodinsky, etc.).

5. **Interactive Solver**: Allow users to add custom fairness constraints (e.g., enforce EF, proportionality).

---

## 10. References

1. **Nash, J. F.** (1950). "The Bargaining Problem." *Econometrica*, 18(2), 155–162.

2. **Moulin, H.** (2003). *Fair Division and Collective Welfare*. MIT Press.

3. **Brams, S. J., & Taylor, A. D.** (1996). *Fair Division: From Cake-Cutting to Dispute Resolution*. Cambridge University Press.

4. **Caragiannis, I., et al.** (2019). "The Unreasonable Fairness of Maximum Nash Welfare." *ACM Transactions on Economics and Computation*, 7(3), 1–32.

5. **Kalai, E.** (1977). "Proportional Solutions to Bargaining Situations: Interpersonal Utility Comparisons." *Econometrica*, 45(7), 1623–1630.

6. **Procaccia, A. D.** (2016). "Cake Cutting Algorithms." In *Handbook of Computational Social Choice*, Cambridge University Press.

---

## 11. Summary

This library implements two theoretically grounded approaches to fair division:

- **Max-Min (Egalitarian)**: Maximizes the minimum (normalized) utility. Prioritizes equity. Pareto efficient. Does not guarantee envy-freeness.

- **Nash Social Welfare**: Maximizes the geometric mean of utilities. Balances efficiency and fairness. Satisfies Nash bargaining axioms. Pareto efficient. Does not guarantee envy-freeness.

Both algorithms are **Pareto efficient** and satisfy **symmetry**. Neither guarantees **envy-freeness**, but we provide comprehensive diagnostics to measure envy and other fairness properties ex-post.

The implementations are production-ready, numerically stable, and thoroughly tested for game-theoretic properties.
