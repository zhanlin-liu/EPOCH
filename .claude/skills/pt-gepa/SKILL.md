---
name: pt-gepa
description: Use when an EPOCH prompt_tune round's hypothesis is reflective prompt evolution with GEPA — the task is hard, DSPy has plateaued, and you want an optimizer that reads failure traces to propose targeted rewrites. Runs gepa.optimize over the TRAIN split and writes the best evolved prompt into system.txt.
---

# pt-gepa

Evolve the prompt with GEPA (Genetic-Pareto reflective evolution), then write the best
candidate into `system.txt`. Implements the standard optimizer contract.

> Requires the `gepa` package. Install into the project env first:
> `uv add --project projects/<slug> gepa`
> Reference: https://github.com/gepa-ai/gepa · paper arXiv:2507.19457

## When to Pick This

- Hard task where DSPy plateaued; you want trace-level reflection, not just demo search.
- Budget for hundreds of metric calls (GEPA reflects on failures to mutate prompts).

## How It Works

1. Seed candidate = the current prompt collapsed into one `system_prompt` (with the
   single-word-final-line instruction preserved).
2. Split TRAIN internally into train/val (TRAIN only — EVAL is never read).
3. `gepa.optimize(seed_candidate, trainset, valset, task_lm, reflection_lm, max_metric_calls)`.
4. Write `result.best_candidate['system_prompt']` → `system.txt`; `task.txt` keeps the
   `{text}` template + single-word output line.

## Config (`--config` JSON)

| Key | Default | Meaning |
|-----|---------|---------|
| `max_metric_calls` | 150 | Evaluation budget (100–500 typical) |
| `reflection_model` | `gpt-4.1-mini` | Model that reflects on failures and proposes rewrites |
| `val_fraction` | 0.3 | Fraction of TRAIN held out internally as GEPA's valset |

The **task model stays locked** to `llm.model`; `reflection_model` only drives evolution.

## Run

```bash
uv add --project projects/<slug> gepa
python .claude/skills/pt-gepa/scripts/optimize.py \
  --project projects/<slug> --train projects/<slug>/data/train.jsonl \
  --prompts projects/<slug>/src/prompts --out projects/<slug>/src/prompts \
  --config '{"max_metric_calls":150,"reflection_model":"gpt-4.1-mini"}' --seed 42
```

## Notes

- TRAIN only — GEPA's valset is carved from TRAIN; EVAL is never touched.
- The data shape passed to GEPA (`input`/`answer` dicts) targets the default adapter; if your
  installed `gepa` version expects a different shape, adjust in `scripts/optimize.py`.
- A single-word-output instruction is re-appended to the evolved prompt as a parser guard.
