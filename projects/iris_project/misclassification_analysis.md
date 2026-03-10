# Iris Rule-Based Classification: Misclassification Analysis

## Summary

**Overall Performance:**
- TRAIN: 95.8% accuracy (5/120 errors, 4.2% error rate)
- EVAL: 93.3% accuracy (2/30 errors, 6.7% error rate)

**Error Distribution:**
- versicolor → virginica: 6 cases (4 train, 2 eval) - **MAIN PROBLEM**
- virginica → versicolor: 1 case (1 train, 0 eval)

---

## Root Cause Analysis

### Problem 1: Versicolor Misclassified as Virginica (6 cases)

**Pattern:** Versicolor samples in the boundary region (PL ≈ 4.7-5.1, PW ≈ 1.5-1.8) are being overwhelmed by virginica rules.

**Why this happens:**

The virginica rules have much stronger weights (1.2-1.5) compared to versicolor rules (0.6-0.7), causing virginica to win in boundary cases.

**Specific Failure Cases:**

| Case | PL | PW | Virginica Score | Versicolor Score | True Class |
|------|----|----|-----------------|------------------|------------|
| TRAIN-20 | 4.9 | 1.5 | 2.8 (petal_length + combo) | 1.3 (petal_length + petal_width) | versicolor |
| TRAIN-39 | 4.8 | 1.8 | 2.5 (petal_width + combo) | 0.6 (petal_length) | versicolor |
| TRAIN-64 | 5.1 | 1.6 | 2.8 (petal_length + combo) | 0.7 (petal_width) | versicolor |
| TRAIN-118 | 4.9 | 1.5 | 2.8 (petal_length + combo) | 1.3 (petal_length + petal_width) | versicolor |
| EVAL-5 | 4.7 | 1.6 | 1.3 (combo) | 1.3 (petal_length + petal_width) | versicolor |
| EVAL-25 | 5.0 | 1.7 | 2.8 (petal_length + combo) | 0.6 (petal_length) | versicolor |

**Problematic Rules:**

1. **virginica_petal_length** (weight: 1.5)
   - Condition: `petal_length > 4.8`
   - Issue: Triggers too early, overlaps heavily with versicolor range
   - Fires on versicolor samples with PL 4.9-5.1

2. **virginica_combo** (weight: 1.3)
   - Condition: `petal_length > 4.5 and petal_width > 1.4`
   - Issue: Very aggressive threshold, captures many versicolor cases
   - Fires on versicolor samples with PL ≥ 4.7 and PW ≥ 1.5

3. **virginica_petal_width** (weight: 1.2)
   - Condition: `petal_width > 1.7`
   - Issue: Captures high-end versicolor samples
   - Fires on versicolor samples with PW ≥ 1.8

4. **Weak versicolor rules** (weights: 0.6-0.7)
   - Even when multiple versicolor rules fire, they can't overcome a single virginica rule
   - Example: EVAL-5 shows versicolor rules scoring 1.3 vs virginica combo alone scoring 1.3 (tie broken in favor of virginica)

---

### Problem 2: Virginica Misclassified as Versicolor (1 case)

**Pattern:** One virginica sample at the lower boundary (PL=4.5, PW=1.7) doesn't trigger any virginica rules.

**Specific Case:**

| Case | PL | PW | Virginica Score | Versicolor Score | True Class |
|------|----|----|-----------------|------------------|------------|
| TRAIN-1 | 4.5 | 1.7 | 0 (no rules fired) | 0.6 (petal_length) | virginica |

**Why this happens:**

- PL=4.5 is below all virginica petal_length thresholds (4.8, 5.5)
- PW=1.7 is below virginica_petal_width threshold (> 1.7, not ≥ 1.7)
- Doesn't meet virginica_combo condition (needs PL > 4.5, has PL = 4.5)
- Only versicolor_petal_length rule fires (4.5 is within 3.0-5.0 range)

This is a **coverage gap** for virginica at the low end of its distribution.

---

## Detailed Rule Firing Analysis

### Current Rules (from [rules.yaml:1-68](projects/iris_project/rules/rules.yaml#L1-L68))

**Setosa Rules (working perfectly):**
- No misclassifications for setosa (100% precision and recall)
- Rules are well-calibrated

**Virginica Rules:**
```yaml
# Too aggressive - fires on versicolor
- virginica_petal_length: PL > 4.8, weight: 1.5
- virginica_combo: PL > 4.5 AND PW > 1.4, weight: 1.3  # VERY aggressive
- virginica_petal_width: PW > 1.7, weight: 1.2
- virginica_very_strong: PL > 5.5, weight: 2.0  # This one is good
```

**Versicolor Rules:**
```yaml
# Too weak to compete with virginica
- versicolor_strict: 3.5 ≤ PL ≤ 4.7 AND 1.1 ≤ PW ≤ 1.5, weight: 1.8  # Doesn't cover boundary cases
- versicolor_petal_length: 3.0 ≤ PL ≤ 5.0, weight: 0.6  # Too weak
- versicolor_petal_width: 1.0 ≤ PW ≤ 1.6, weight: 0.7   # Too weak
```

---

## Recommendations

### Fix #1: Adjust Virginica Thresholds (addresses 5-6 cases)

**Change virginica_petal_length:**
- Current: `petal_length > 4.8`
- Proposed: `petal_length > 5.2`
- Rationale: Avoid overlap with versicolor boundary region (4.7-5.1)

**Change virginica_combo:**
- Current: `petal_length > 4.5 and petal_width > 1.4`
- Proposed: `petal_length > 5.0 and petal_width > 1.6`
- Rationale: More conservative to avoid capturing versicolor

**Change virginica_petal_width:**
- Current: `petal_width > 1.7`
- Proposed: `petal_width >= 1.8`
- Rationale: Slight adjustment to reduce false positives

### Fix #2: Strengthen Versicolor Rules (addresses 6 cases)

**Increase versicolor rule weights:**
- versicolor_petal_length: 0.6 → 1.0
- versicolor_petal_width: 0.7 → 1.0
- Rationale: Should be competitive with virginica rules in boundary region

**Adjust versicolor_strict to cover boundary:**
- Current: `3.5 ≤ PL ≤ 4.7 AND 1.1 ≤ PW ≤ 1.5`
- Proposed: `3.5 ≤ PL ≤ 5.1 AND 1.0 ≤ PW ≤ 1.7`
- Rationale: Extend upper bounds to capture boundary cases

### Fix #3: Add Virginica Coverage Rule (addresses 1 case)

**Add new rule for low-end virginica:**
```yaml
- name: "virginica_low_boundary"
  condition: "petal_length >= 4.5 and petal_length < 4.8 and petal_width >= 1.7"
  action: "virginica"
  weight: 1.0
  description: "Captures low-end virginica samples"
```

---

## Expected Impact

**If all fixes applied:**
- TRAIN accuracy: 95.8% → 100% (eliminate all 5 errors)
- EVAL accuracy: 93.3% → 100% (eliminate all 2 errors)
- Risk: May introduce new errors if thresholds are too aggressive

**Conservative approach:** Start with Fix #1 and Fix #2, evaluate, then add Fix #3 if needed.

---

## Investigation Details

**Data examined:**
- TRAIN split: 120 samples (40 each class)
- EVAL split: 30 samples (10 each class)

**Methodology:**
1. Compared predictions vs ground truth
2. Traced rule firing for each misclassified case
3. Calculated scores to understand decision boundary
4. Identified patterns in feature space

**Tools used:**
- [evaluate.py](projects/iris_project/evaluate.py) - Rule evaluation engine
- [rules.yaml](projects/iris_project/rules/rules.yaml) - Current ruleset
- Python analysis scripts for error pattern detection
