## Round 3: Add Few-Shot Examples

### Changes
- Added examples.txt: 6 few-shot examples from TRAIN covering ambiguous fragments and complex negation patterns

### Metrics

| Metric | Baseline | Proposed | Delta | Threshold | Status |
|--------|----------|----------|-------|-----------|--------|
| eval_accuracy | 0.9167 | 1.0000 | +0.0833 | >=0.02 | ACCEPT |
| train_accuracy | 0.8500 | 0.9000 | +0.0500 | - | - |

### EVAL Leakage Check: PASS
All few-shot examples sourced from TRAIN split only.

### Verdict: ACCEPT

**Evidence:**
eval_accuracy improved +0.0833 to perfect 1.00 (>= min_delta 0.02)
No EVAL leakage — examples are from TRAIN data only
Train-eval gap: -0.10 (eval > train, no overfitting concern)
