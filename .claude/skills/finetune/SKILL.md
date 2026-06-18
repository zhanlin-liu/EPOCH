---
name: finetune
description: Use when investigating an EPOCH finetune round — reading TRAIN metrics and the train/eval gap to diagnose over- or under-fitting, then proposing one hyperparameter change with rationale, without inspecting the EVAL split.
---

# Finetune

Diagnose an ML model's fit from TRAIN metrics and propose one hyperparameter change. The
investigator's technique for `finetune` rounds — ends at a written hypothesis, not a run.

> Deep round workflow: see `skills/epoch/references/finetune.md`. This skill is the
> investigator's hands-on diagnosis technique within that workflow.

## When to Use

- The investigator is analyzing a `finetune` round.
- You have TRAIN metrics (and the prior round's eval) and need to pick one knob to turn.

## Split Discipline

- **TRAIN split only** for diagnosis. The train/eval *gap* uses the prior round's already-
  reported eval number — never inspect new EVAL data here.

## Diagnosis → Knob

| Signal | Reading | Typical change |
|--------|---------|----------------|
| High train, low eval (large gap) | Overfitting | ↑ regularization, ↓ epochs/lr, ↑ dropout |
| Low train and low eval | Underfitting | ↑ capacity/epochs, ↑ lr, ↓ regularization |
| Train still improving at last epoch | Undertrained | ↑ epochs / ↑ lr |
| Unstable/diverging loss | lr too high | ↓ lr, add warmup |

## Process

1. Read TRAIN metrics + the previous round's eval metric.
2. Run `scripts/fit_diagnosis.py` to classify over/under-fit from the gap.
3. Propose **one** hyperparameter change targeting the diagnosis, with rationale.

## Scripts

- `scripts/fit_diagnosis.py` — classify fit from train vs. eval metric.
  ```bash
  python scripts/fit_diagnosis.py --train 0.94 --eval 0.81 --gap-threshold 0.08
  ```

## Common Mistakes

- Changing several hyperparameters at once — one knob per round or attribution is lost.
- Inspecting fresh EVAL data to diagnose — use the prior round's reported eval only.
