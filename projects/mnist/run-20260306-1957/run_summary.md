# Run Summary: run-20260306-1957

## Project: MobileNetV2 MNIST Classifier
**Task type**: finetune
**Model**: MobileNetV2 (pretrained ImageNet, classifier head fine-tuned)
**Dataset**: MNIST subset (10 classes, 200 train, 60 eval)
**Training**: 3 epochs, seed=42, device=mps

## Tunable Parameters
- `optimizer`: [adam, adamw, sgd]
- `learning_rate`: [0.0001, 0.01]

## Metrics Progression

| Round | Optimizer | LR | eval_accuracy | train_accuracy | Gap | Status |
|-------|-----------|------|--------------|----------------|------|--------|
| 1 (Baseline) | adam | 0.001 | 0.5333 | 0.6050 | 0.0717 | Baseline |
| 2 | adamw | 0.005 | 0.6167 | 0.7100 | 0.0933 | ACCEPT (+0.0834) |
| 3 | adamw | 0.01 | 0.5500 | 0.6700 | 0.1200 | REJECT (-0.0667) |
| 3 (retry) | sgd | 0.008 | **0.6667** | 0.7050 | 0.0383 | ACCEPT (+0.0500) |

## What Worked

**Round 2 — AdamW + higher LR (+0.0834)**
- Switched from Adam to AdamW for better weight regularization
- Increased LR from 0.001 to 0.005 to address underfitting
- Both train and eval metrics improved significantly

**Round 3 Retry — SGD with momentum (+0.0500)**
- After AdamW failed at LR=0.01 (training instability), switched to SGD+momentum
- SGD handled higher LR (0.008) more stably
- Best generalization: train-eval gap dropped from 0.09 to 0.04

## What Failed

**Round 3 Initial — LR too aggressive (REJECTED)**
- LR=0.01 with AdamW caused epoch 1 loss to spike (4.24 vs 2.72)
- Model did not recover within 3 epochs
- Lesson: AdamW is less stable than SGD at high LR with limited epochs

## Configuration

- max_rounds: 3 (all used)
- max_retries_per_round: 1 (1 retry used in round 3)
- min_delta: 0.02
- Primary metric: accuracy

## Conclusion

Improved eval accuracy from 0.5333 to 0.6667 (+0.1334, +25.0%) across 3 rounds with 1 rejection and retry. The framework demonstrated adaptive strategy selection: it identified underfitting, tried increasing LR aggressively, detected the resulting instability, and recovered by switching optimizer families. The SGD+momentum configuration provided the best balance of learning speed and stability under a constrained 3-epoch budget.
