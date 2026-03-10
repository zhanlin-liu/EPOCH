## Round 3 (Retry 1): Hyperparameter Tuning Results

### Previous Attempt (Rejected)
- LR=0.01 with AdamW caused training instability (epoch 1 loss spiked to 4.24)
- eval_accuracy regressed from 0.6167 to 0.5500

### Retry Changes
- optimizer: adamw → sgd (with momentum=0.9, handles higher LR better)
- learning_rate: 0.01 → 0.008 (slightly reduced from failed attempt)

### Metrics

| Metric | Baseline (R2) | Proposed | Delta | Constraint | Status |
|--------|----------|----------|-------|------------|--------|
| eval_accuracy | 0.6167 | 0.6667 | +0.0500 | ≥0.02 | ✅ |
| train_accuracy | 0.7100 | 0.7050 | -0.0050 | - | - |
| train_eval_gap | 0.0933 | 0.0383 | -0.0550 | <0.15 | ✅ |
| eval_loss | 1.2339 | 1.4016 | +0.1677 | - | - |

### Verdict: ✅ ACCEPT

**Evidence:**
eval_accuracy improved +0.05, exceeding min_delta of 0.02. Train-eval gap narrowed dramatically from 0.09 to 0.04, indicating much better generalization. SGD+momentum provided more stable training at higher LR — epoch 1 loss was 2.22 (vs 4.24 with AdamW at LR=0.01).
