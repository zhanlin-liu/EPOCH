# Run Summary: run-20260306-1400

## Project: Sentiment Analysis Prompt Tuner
**Task type**: prompt_tune
**Model**: gpt-4.1-mini
**Dataset**: SST-2 (binary sentiment)
**Subset**: 20 train (10/class), 12 eval (6/class)

## Metrics Progression

| Round | eval_accuracy | train_accuracy | Status |
|-------|--------------|----------------|--------|
| 1 (Baseline) | **1.0000** | 0.8500 | Baseline |

## Result

**Optimization complete after Round 1.** The baseline prompt achieves perfect eval accuracy (1.00), leaving no room for improvement (min_delta = 0.02). No further rounds are needed.

## Train Failures (3/20)

The 3 train misclassifications are ambiguous sentence fragments where the ground truth labels are debatable:

| Index | Text | Expected | Predicted |
|-------|------|----------|-----------|
| 1 | "a deeper story" | positive | negative |
| 6 | "an era of theatrical comedy that, while past," | positive | negative |
| 9 | "its opening" | positive | negative |

All three are very short fragments lacking clear sentiment signal. The LLM's negative predictions are arguably reasonable.

## Configuration

- max_rounds: 5 (used 1)
- max_retries_per_round: 1
- min_delta: 0.02
- Primary metric: accuracy

## Conclusion

Binary sentiment classification (positive/negative) on SST-2 is too easy for gpt-4.1-mini — even a plain baseline prompt achieves 100% eval accuracy on a 12-sample subset. Consider:
- Using a harder dataset (e.g., fine-grained sentiment, sarcasm detection)
- Increasing subset size to surface more challenging examples
- Using a weaker model to create more room for prompt optimization
