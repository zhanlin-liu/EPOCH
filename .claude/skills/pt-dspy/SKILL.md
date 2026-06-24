---
name: pt-dspy
description: Use when an EPOCH prompt_tune round's hypothesis is automatic joint instruction-and-demo optimization with DSPy — cheaper methods have plateaued and there is budget for many LLM calls. Runs MIPROv2 or BootstrapFewShot over the TRAIN split and flattens the compiled instruction + demos into the prompt files.
---

# pt-dspy

Compile the prompt with DSPy's optimizers (MIPROv2 / BootstrapFewShot), then flatten the
result into `system.txt` + `examples.txt`. Implements the standard optimizer contract.

> Requires the `dspy` package. Install into the project env first:
> `uv add --project projects/<slug> dspy-ai`

## When to Pick This

- Few-shot / CoT / system-refinement have plateaued.
- You have budget for hundreds of LLM calls (MIPROv2 searches instructions + demos jointly).

## How It Works

1. Build a generic DSPy `Signature` (`text -> label`) and a `dspy.Predict` student.
2. Convert TRAIN rows into `dspy.Example`s (TRAIN only).
3. Run the chosen optimizer's `.compile(student, trainset=...)` with an exact-match metric.
4. Extract the optimized **instruction** (`signature.get_instructions()`) and **demos**
   (`predictor.demos`), and flatten them: instruction → `system.txt`, demos → `examples.txt`,
   `task.txt` keeps the `{text}` template + single-word output line.

Flattening is intentional (approved design): DSPy normally owns inference, but EPOCH evaluates
through the project's `evaluate.py`, so we serialize the compiled program into the prompt files.

## Config (`--config` JSON)

| Key | Default | Meaning |
|-----|---------|---------|
| `optimizer` | `MIPROv2` | `MIPROv2` or `BootstrapFewShot` |
| `auto` | `light` | MIPROv2 budget: `light` / `medium` / `heavy` |
| `max_bootstrapped_demos` | 4 | Bootstrapped demos cap |
| `max_labeled_demos` | 4 | Labeled demos cap |
| `optimizer_model` | `gpt-4.1-mini` | Instruction-proposal model (`prompt_model`) |

The **task model stays locked** to `llm.model`; `optimizer_model` only proposes instructions.

## Run

```bash
uv add --project projects/<slug> dspy-ai
python .claude/skills/pt-dspy/scripts/optimize.py \
  --project projects/<slug> --train projects/<slug>/data/train.jsonl \
  --prompts projects/<slug>/src/prompts --out projects/<slug>/src/prompts \
  --config '{"optimizer":"MIPROv2","auto":"light","max_bootstrapped_demos":4}' --seed 42
```

## Notes

- TRAIN only — the optimizer splits TRAIN internally for its validation signal; EVAL is never read.
- Cost scales with `auto`; start `light`. On tiny TRAIN sets MIPROv2 may warn — reduce demos.
