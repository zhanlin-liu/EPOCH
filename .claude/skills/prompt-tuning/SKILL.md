---
name: prompt-tuning
description: Use when investigating LLM prompt failures in an EPOCH prompt_tune round — sampling TRAIN-split failures, identifying a failure pattern, and proposing one targeted prompt edit with rationale, without inspecting the EVAL split.
---

# Prompt Tuning

Diagnose why an LLM prompt fails on the TRAIN split and propose one targeted edit. This is
the investigator's technique for `prompt_tune` rounds — it ends at a written hypothesis,
not at an implemented change.

## When to Use

- The investigator is analyzing a `prompt_tune` round.
- You have failing examples and need to find the pattern behind them.

## Split Discipline

- **TRAIN split only.** Never read EVAL examples — diagnosing against EVAL is overfitting.

## Process

1. Sample failing TRAIN examples (`investigation.samples` from `epoch_run.yaml`).
2. Group failures by symptom (format errors, missing constraints, ambiguous instructions, hallucinations).
3. Identify the single dominant pattern.
4. Propose **one** prompt edit that targets it, with rationale tying edit → pattern.

## Common Failure Patterns → Edits

| Pattern | Typical edit |
|---------|--------------|
| Output format drifts | Add an explicit format spec + one example |
| Ignores a constraint | State the constraint as a hard rule, early |
| Ambiguous on edge cases | Add a decision rule for the edge case |
| Hallucinates facts | Add "only use provided context; say 'unknown' otherwise" |
| Over-verbose | Add a length/structure bound |

## Scripts

- `scripts/sample_failures.py` — sample N failing rows from a TRAIN predictions file
  (expects rows with `input`, `expected`, `predicted`, `correct`).
  ```bash
  python scripts/sample_failures.py --preds train_preds.jsonl --n 10
  ```

## Common Mistakes

- Proposing several edits at once — one hypothesis per round; bundle = no attribution.
- Reading EVAL examples to "understand the task better" — breaks the split.
- Rewriting the whole prompt — large rewrites make the metric delta unattributable.
