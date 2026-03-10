## Round 3: Widen Sepal Width Boundary

### Changes
- Rule 3: `sepal_width < 3.0` → `sepal_width <= 3.0`
- Two virginica samples at exactly sw=3.0 were being excluded from the rule

### Metrics

| Metric | Baseline (R2) | Proposed | Delta | Constraint | Status |
|--------|----------|----------|-------|------------|--------|
| eval_accuracy | 1.0000 | 1.0000 | 0.0000 | ≥0.01 | — |
| train_accuracy | 0.9619 | 0.9810 | +0.0191 | - | ✅ |
| train_failures | 4 | 2 | -2 | - | - |

### Verdict: ✅ ACCEPT

**Evidence:**
eval remains perfect. Train improved by fixing 2 virginica samples at the sw=3.0 boundary. Remaining 2 train failures are genuinely conflicting boundary cases (versicolor with pl≥5.0).
