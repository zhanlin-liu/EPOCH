## Round 1: Baseline Establishment (gpt-4.1-nano)

### Changes
- Switched model from gpt-4.1-mini to gpt-4.1-nano for optimization headroom
- Plain baseline prompt: system instructions + task template
- New run ID: run-20260306-1500

### Metrics

| Metric | Value |
|--------|-------|
| eval_accuracy | 0.8333 |
| eval_correct | 10/12 |
| train_accuracy | 0.8000 |
| train_correct | 16/20 |

### Data Split
- Train: 20 samples (10 negative, 10 positive)
- Eval: 12 samples (6 negative, 6 positive)
