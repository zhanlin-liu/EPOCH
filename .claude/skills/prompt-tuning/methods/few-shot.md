# Method: few-shot

Select K demonstration examples from TRAIN and write them to `examples.txt`. Implements the
standard optimizer contract (see the router `SKILL.md`).

**Pick when:** the model grasps the task but is inconsistent or drifts on format; cheap first/second round.

**Script:** `scripts/few_shot.py`

**Config (`--config` JSON):**

| Key | Default | Meaning |
|-----|---------|---------|
| `k` | 4 | Total demos (balanced across classes) |
| `selection` | `"balanced"` | `"balanced"` (random per class, seeded) or `"hard-balanced"` (prefer currently-misclassified TRAIN examples — costs K' LLM calls) |

**Run:**
```bash
python .claude/skills/prompt-tuning/scripts/few_shot.py \
  --project projects/<slug> --train projects/<slug>/data/train.jsonl \
  --prompts projects/<slug>/src/prompts --out projects/<slug>/src/prompts \
  --config '{"k":4,"selection":"balanced"}' --seed 42
```

Writes `examples.txt` (prepended to the task prompt by `evaluate.py`) + `optimize_report.json`.

**Notes:** TRAIN only. `"hard-balanced"` runs the current prompt over TRAIN to find hard
cases — still never touches EVAL. Keep K small on tiny TRAIN sets.
