---
name: ml-evaluation
description: Use when running an EPOCH round's evaluation — executing EVAL on the held-out split, computing metric deltas against the previous round, and writing the metrics and delta artifacts without rendering an accept/reject verdict.
---

# ML Evaluation

Produce a round's numbers: run EVAL, compare to the previous round, write the artifacts.
The verdict belongs to the reviewer — this skill stops at the metrics.

## When to Use

- The evaluator is scoring a proposed change.
- Computing the delta between two metrics files.

## Splits (critical)

- **EVAL split only.** Never inspect or leak TRAIN data here, and never expose EVAL
  examples — that would let later rounds overfit.
- Deterministic tasks (rule_based) may use the full dataset.

This separation is what prevents overfitting to the evaluation set across rounds.

## Process

1. Run `EVAL_CMD` (from `epoch_run.yaml`) → produces `round_N_proposed_metrics.json`.
2. Load the previous round's metrics.
3. Compute deltas → write `delta_round_N.json`.
4. Hand the artifacts to the reviewer. Render **no** accept/reject decision.

## Artifacts

| File | Contents |
|------|----------|
| `round_N_proposed_metrics.json` | Metrics from this round's EVAL run |
| `delta_round_N.json` | Per-metric old → new → delta vs. previous round |

## Scripts

- `scripts/compute_delta.py` — diff two metrics JSON files into a delta artifact.
  ```bash
  python scripts/compute_delta.py \
    --baseline baseline_metrics.json \
    --proposed round_3_proposed_metrics.json \
    --out delta_round_3.json
  ```

## Common Mistakes

- Touching TRAIN data during evaluation — breaks the split guarantee.
- Printing EVAL examples into logs or reports — leaks the held-out set.
- Deciding accept/reject here — that is the reviewer's call, on these numbers.
