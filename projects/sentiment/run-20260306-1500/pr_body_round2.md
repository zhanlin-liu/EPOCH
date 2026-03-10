## Round 2: System Prompt Refinement

### Changes
- Modified system.txt: Added movie review context, guidance for ambiguous fragments, and negation handling instructions

### Metrics

| Metric | Baseline | Proposed | Delta | Threshold | Status |
|--------|----------|----------|-------|-----------|--------|
| eval_accuracy | 0.8333 | 0.9167 | +0.0834 | >=0.02 | ACCEPT |
| train_accuracy | 0.8000 | 0.8500 | +0.0500 | - | - |

### EVAL Leakage Check: PASS

### Verdict: ACCEPT

**Evidence:**
eval_accuracy improved +0.0834 (>= min_delta 0.02)
No EVAL leakage detected — prompt contains no EVAL-specific text
Train-eval gap: 0.035 (good generalization)
