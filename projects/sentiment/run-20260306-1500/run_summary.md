# Run Summary: run-20260306-1500

## Project: Sentiment Analysis Prompt Tuner
**Task type**: prompt_tune
**Model**: gpt-4.1-nano
**Dataset**: SST-2 (binary sentiment)
**Subset**: 20 train (10/class), 12 eval (6/class)

## Metrics Progression

| Round | eval_accuracy | train_accuracy | Change | Status |
|-------|--------------|----------------|--------|--------|
| 1 (Baseline) | 0.8333 | 0.8000 | — | Baseline |
| 2 | 0.9167 | 0.8500 | +0.0834 | ACCEPT |
| 3 | **1.0000** | 0.9000 | +0.0833 | ACCEPT |

## What Worked

**Round 2 — System prompt refinement (+0.0834)**
- Added movie review context to system prompt
- Added guidance for interpreting ambiguous fragments
- Added negation handling instructions

**Round 3 — Few-shot examples (+0.0833)**
- Added 6 examples from TRAIN covering ambiguous fragments and complex sentences
- Examples demonstrated that short/neutral phrases can be positive in movie review context

## Remaining Train Failures (2/20)

| Index | Text | Expected | Predicted |
|-------|------|----------|-----------|
| 6 | "an era of theatrical comedy that, while past," | positive | negative |
| 9 | "its opening" | positive | negative |

These are extremely ambiguous fragments where the ground truth labels are debatable.

## Configuration

- max_rounds: 5 (used 3)
- max_retries_per_round: 1 (no retries needed)
- min_delta: 0.02
- Primary metric: accuracy

## Conclusion

Achieved perfect eval accuracy (1.00) in 3 rounds, improving from 0.83 baseline. The two key techniques were:
1. Domain-specific system prompt (movie review context + fragment handling)
2. Few-shot examples from the training set
