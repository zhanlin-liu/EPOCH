# Method: chain-of-thought

Reformat the task prompt so the model reasons for 1–3 sentences, then outputs the label on
its own final line. Deterministic — **zero LLM calls**. Standard optimizer contract.

**Pick when:** TRAIN failures involve reasoning a direct prompt skips — negation, contrast
("not X but Y"), comparison, implied sentiment. Cheap early-round move.

**Script:** `scripts/chain_of_thought.py`

**Critical invariant:** the rewritten prompt MUST end with a single-word label on the final
line so `evaluate.py` (last-non-empty-line parse) still works. The script enforces this.

**Config (`--config` JSON):**

| Key | Default | Meaning |
|-----|---------|---------|
| `max_sentences` | 3 | Cap on reasoning length |
| `final_line_hint` | `"Reasoning and sentiment:"` | Cue placed before the model's reply |

**Run:**
```bash
python .claude/skills/prompt-tuning/scripts/chain_of_thought.py \
  --project projects/<slug> --train projects/<slug>/data/train.jsonl \
  --prompts projects/<slug>/src/prompts --out projects/<slug>/src/prompts \
  --config '{"max_sentences":3}' --seed 42
```

Rewrites `task.txt` (preserving `{text}`) + `optimize_report.json`.

**Notes:** TRAIN only. If rejected, escalate to system-refinement or dspy rather than
re-applying CoT.
