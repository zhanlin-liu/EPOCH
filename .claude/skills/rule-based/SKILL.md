---
name: rule-based
description: Use when investigating an EPOCH rule_based round — analyzing false positives and false negatives from predictions to find the one rule or threshold to adjust, proposing a single targeted change with rationale.
---

# Rule-Based

Diagnose where a rule system errs and propose one rule/threshold change. The investigator's
technique for `rule_based` rounds.

> Deep round workflow: see `skills/epoch/references/rule_based.md`. This skill is the
> investigator's hands-on diagnosis technique within that workflow.

## When to Use

- The investigator is analyzing a `rule_based` round.
- You have predictions with errors and need to pick one rule or threshold to change.

## Data Access

- Deterministic task: **full dataset access** is allowed (no TRAIN/EVAL hiding for rule_based).

## Diagnosis → Change

| Error skew | Reading | Typical change |
|------------|---------|----------------|
| Many false positives | Rule fires too eagerly | Tighten condition / raise threshold |
| Many false negatives | Rule misses cases | Loosen condition / lower threshold / add a clause |
| Errors cluster on one rule | That rule is miscalibrated | Adjust that rule only |
| Conflicting rules | Ordering/precedence issue | Reorder or add a guard |

## Process

1. Run `scripts/confusion.py` on predictions to get FP/FN counts (overall or per rule).
2. Identify the single rule/threshold driving most error.
3. Propose **one** targeted change, with rationale.

## Scripts

- `scripts/confusion.py` — compute TP/FP/FN/TN and precision/recall from a predictions
  file (JSONL rows with `expected` and `predicted` booleans; optional `rule` field for
  per-rule breakdown).
  ```bash
  python scripts/confusion.py --preds preds.jsonl --by-rule
  ```

## Common Mistakes

- Adjusting multiple rules in one round — one change, so the metric delta is attributable.
- Chasing a few outliers instead of the dominant error cluster.
