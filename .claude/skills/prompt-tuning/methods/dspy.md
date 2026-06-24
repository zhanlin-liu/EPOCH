# Method: dspy

Compile the prompt with DSPy's optimizers (MIPROv2 / BootstrapFewShot), then flatten the
result into `system.txt` + `examples.txt`. Standard optimizer contract.

> Requires `dspy`: `uv add --project projects/<slug> dspy-ai`

**Pick when:** few-shot/CoT/system-refinement plateaued and there is budget for hundreds of
LLM calls (MIPROv2 searches instructions + demos jointly).

**Script:** `scripts/dspy_optimize.py`

**How it works:** build a generic `Signature` (`text -> label`) + `dspy.Predict` student →
convert TRAIN rows to `dspy.Example`s → run `.compile()` with an exact-match metric → extract
the optimized instruction (`signature.get_instructions()`) and demos (`predictor.demos`) →
flatten: instruction → `system.txt`, demos → `examples.txt`, `task.txt` keeps `{text}`.
Flattening is intentional (EPOCH evaluates through the project's `evaluate.py`).

**Config (`--config` JSON):**

| Key | Default | Meaning |
|-----|---------|---------|
| `optimizer` | `MIPROv2` | `MIPROv2` or `BootstrapFewShot` |
| `auto` | `light` | MIPROv2 budget: `light`/`medium`/`heavy` |
| `max_bootstrapped_demos` | 4 | Bootstrapped demos cap |
| `max_labeled_demos` | 4 | Labeled demos cap |
| `optimizer_model` | `gpt-4.1-mini` | Instruction-proposal model (`prompt_model`) |

Task model stays locked to `llm.model`; `optimizer_model` only proposes instructions.

**Run:**
```bash
uv add --project projects/<slug> dspy-ai
python .claude/skills/prompt-tuning/scripts/dspy_optimize.py \
  --project projects/<slug> --train projects/<slug>/data/train.jsonl \
  --prompts projects/<slug>/src/prompts --out projects/<slug>/src/prompts \
  --config '{"optimizer":"MIPROv2","auto":"light"}' --seed 42
```

**Notes:** TRAIN only — the optimizer splits TRAIN internally; EVAL is never read. Cost scales
with `auto`; start `light`. Reference: https://dspy.ai/api/optimizers/MIPROv2/
