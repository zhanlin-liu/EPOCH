---
name: pt-system-refinement
description: Use when an EPOCH prompt_tune round's hypothesis is refining the instructions themselves — the system/task prompt is vague, ambiguous, or contradictory. Runs the current prompt over TRAIN to collect failures, then uses an LLM prompt-engineer call to rewrite system.txt/task.txt, preserving the output contract.
---

# pt-system-refinement

Use an LLM "prompt engineer" to rewrite the instructions based on the current prompt's TRAIN
failures. Implements the standard optimizer contract.

## When to Pick This

- The instructions are the problem: ambiguous wording, missing constraints, conflicting rules.
- Few-shot / CoT didn't help and you suspect the instruction text, not the reasoning shape.

## How It Works

1. Run the current prompt over TRAIN → collect misclassified examples (TRAIN only).
2. Send the current `system.txt` + `task.txt` + a failure summary to the optimizer model and
   ask for improved instructions.
3. Write the rewritten `system.txt` / `task.txt`, preserving `{text}` and the single-word
   final-line output contract.

## Config (`--config` JSON)

| Key | Default | Meaning |
|-----|---------|---------|
| `optimizer_model` | `gpt-4.1-mini` | Model that rewrites the prompt (NOT the locked task model) |
| `max_failures` | 8 | How many TRAIN failures to summarize into the rewrite request |

## Run

```bash
python .claude/skills/pt-system-refinement/scripts/optimize.py \
  --project projects/<slug> --train projects/<slug>/data/train.jsonl \
  --prompts projects/<slug>/src/prompts --out projects/<slug>/src/prompts \
  --config '{"optimizer_model":"gpt-4.1-mini","max_failures":8}' --seed 42
```

Rewrites `system.txt` and `task.txt`, writes `optimize_report.json`.

## Notes

- The task model stays locked; only the *rewriting* uses `optimizer_model`.
- The script asserts `{text}` survives and the instruction still demands a single-word label.
- TRAIN only — failures are computed on TRAIN; EVAL is never read.
