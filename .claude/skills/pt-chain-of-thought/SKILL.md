---
name: pt-chain-of-thought
description: Use when an EPOCH prompt_tune round's hypothesis is chain-of-thought — failures need multi-step reasoning (negation, contrast like "not X but Y", comparisons) that a direct-answer prompt skips. Rewrites task.txt to reason briefly then emit a single-word label on the final line.
---

# pt-chain-of-thought

Reformat the task prompt so the model reasons for 1–3 sentences, then outputs the label on
its own final line. Deterministic text transform — **zero LLM calls**. Implements the
standard optimizer contract.

## When to Pick This

- TRAIN failures involve reasoning the direct prompt skips: negation, contrast ("not X but
  Y"), comparison, implied sentiment.
- Cheap first/second-round move before reaching for DSPy/GEPA.

## Critical Invariant

The rewritten prompt MUST end with a single-word label on the final line, so `evaluate.py`
(which reads the last non-empty line) still parses. The script enforces this.

## Config (`--config` JSON)

| Key | Default | Meaning |
|-----|---------|---------|
| `max_sentences` | 3 | Cap on reasoning length |
| `final_line_hint` | `"Reasoning and sentiment:"` | The cue placed before the model's reply |

## Run

```bash
python .claude/skills/pt-chain-of-thought/scripts/optimize.py \
  --project projects/<slug> --train projects/<slug>/data/train.jsonl \
  --prompts projects/<slug>/src/prompts --out projects/<slug>/src/prompts \
  --config '{"max_sentences":3}' --seed 42
```

Rewrites `task.txt` (preserving `{text}`) and writes `optimize_report.json`.

## Notes

- Does not read data beyond confirming label names for the instruction; TRAIN only.
- If the round is rejected, escalate to `pt-system-refinement` or `pt-dspy` rather than
  re-applying CoT.
