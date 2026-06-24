---
name: pt-few-shot
description: Use when an EPOCH prompt_tune round's hypothesis is few-shot example selection — the model grasps the task but needs concrete demonstrations, or output format drifts. Selects balanced (optionally hardness-weighted) demos from the TRAIN split and writes them to examples.txt.
---

# pt-few-shot

Select K demonstration examples from TRAIN and write them to `examples.txt`. Implements the
standard optimizer contract (see the `prompt-tuning` router).

## When to Pick This

- Failures look like the model *can* do the task but is inconsistent or drifts on format.
- First or second optimization round (cheap, fast).

## Config (`--config` JSON)

| Key | Default | Meaning |
|-----|---------|---------|
| `k` | 4 | Total demos (balanced across classes) |
| `selection` | `"balanced"` | `"balanced"` (random per class, seeded) or `"hard-balanced"` (prefer currently-misclassified TRAIN examples — costs K' LLM calls to score) |

## Run

```bash
python .claude/skills/pt-few-shot/scripts/optimize.py \
  --project projects/<slug> --train projects/<slug>/data/train.jsonl \
  --prompts projects/<slug>/src/prompts --out projects/<slug>/src/prompts \
  --config '{"k":4,"selection":"balanced"}' --seed 42
```

Writes `examples.txt` (prepended to the task prompt by `evaluate.py`) and `optimize_report.json`.

## Notes

- TRAIN only. `"hard-balanced"` runs the current prompt over TRAIN to find hard cases — it
  still never touches EVAL.
- Keep K small on tiny TRAIN sets; demos come out of the same pool you evaluate patterns on.
