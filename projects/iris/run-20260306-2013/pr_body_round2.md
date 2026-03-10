## Round 2: Refine Versicolor/Virginica Boundary

### Changes
- Changed `petal_length > 5.0` to `petal_length >= 5.0` to capture boundary virginica samples
- Replaced aggressive `petal_width > 1.5` with `petal_width >= 1.7 and sepal_width < 3.0`
- Added sepal_width as a tiebreaker: versicolor with wide petals tends to also have wide sepals (≥3.0)

### Metrics

| Metric | Baseline | Proposed | Delta | Constraint | Status |
|--------|----------|----------|-------|------------|--------|
| eval_accuracy | 0.9778 | 1.0000 | +0.0222 | ≥0.01 | ✅ |
| train_accuracy | 0.9524 | 0.9619 | +0.0095 | - | - |

### Verdict: ✅ ACCEPT

**Evidence:**
Perfect eval accuracy. Train failures reduced from 5 to 4, all on genuinely overlapping boundary cases. No EVAL-specific rules — sepal_width tiebreaker is a general pattern observed in TRAIN failures.
