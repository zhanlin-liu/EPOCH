# Method: gepa

Evolve the prompt with GEPA (Genetic-Pareto reflective evolution), then write the best
candidate into `system.txt`. Standard optimizer contract.

> Requires `gepa`: `uv add --project projects/<slug> gepa`
> Reference: https://github.com/gepa-ai/gepa · paper arXiv:2507.19457

**Pick when:** hard task where DSPy plateaued; you want trace-level reflection (GEPA reads
failure traces to mutate prompts), with budget for hundreds of metric calls.

**Script:** `scripts/gepa_optimize.py`

**How it works:** seed candidate = current prompt collapsed into one `system_prompt` (single-
word instruction preserved) → split TRAIN internally into train/val (TRAIN only) →
`gepa.optimize(seed_candidate, trainset, valset, task_lm, reflection_lm, max_metric_calls)` →
write `result.best_candidate['system_prompt']` → `system.txt`; `task.txt` keeps `{text}`.

**Config (`--config` JSON):**

| Key | Default | Meaning |
|-----|---------|---------|
| `max_metric_calls` | 150 | Evaluation budget (100–500 typical) |
| `reflection_model` | `gpt-4.1-mini` | Model that reflects on failures and proposes rewrites |
| `val_fraction` | 0.3 | Fraction of TRAIN held out internally as GEPA's valset |

Task model stays locked to `llm.model`; `reflection_model` only drives evolution.

**Run:**
```bash
uv add --project projects/<slug> gepa
python .claude/skills/prompt-tuning/scripts/gepa_optimize.py \
  --project projects/<slug> --train projects/<slug>/data/train.jsonl \
  --prompts projects/<slug>/src/prompts --out projects/<slug>/src/prompts \
  --config '{"max_metric_calls":150,"reflection_model":"gpt-4.1-mini"}' --seed 42
```

**Notes:** TRAIN only — GEPA's valset is carved from TRAIN. The data shape (`input`/`answer`
dicts) targets the default adapter; adjust in the script if your `gepa` version differs. A
single-word-output instruction is re-appended as a parser guard.
