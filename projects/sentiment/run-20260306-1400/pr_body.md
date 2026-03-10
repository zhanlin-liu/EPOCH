## Round 1: Baseline Establishment

### Changes
- Scaffolded sentiment classification project with SST-2 dataset
- Created `prepare_data.py` for balanced subset sampling (seed 42)
- Created `evaluate.py` with async OpenAI inference (gpt-4.1-mini)
- Plain baseline prompt: system instructions + task template

### Metrics

| Metric | Value |
|--------|-------|
| eval_accuracy | 1.0000 |
| eval_correct | 12/12 |
| train_accuracy | 0.8500 |
| train_correct | 17/20 |

### Data Split
- Train: 20 samples (10 negative, 10 positive)
- Eval: 12 samples (6 negative, 6 positive)

### Notes
Eval accuracy is already perfect (1.00) with a basic prompt. GPT-4.1-mini handles binary sentiment classification trivially at this sample size. Train accuracy (0.85) shows 3 failures that could be investigated for prompt improvement, but eval has no room to improve.
