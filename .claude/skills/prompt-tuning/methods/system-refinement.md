# Method: system-refinement

Use an LLM "prompt engineer" to rewrite the instructions from the current prompt's TRAIN
failures. Standard optimizer contract.

**Pick when:** the instructions are the problem — ambiguous wording, missing constraints,
conflicting rules; few-shot/CoT didn't help.

**Script:** `scripts/system_refinement.py`

**How it works:** run the current prompt over TRAIN → collect misclassified examples → send
current `system.txt`/`task.txt` + failure summary to the optimizer model → write rewritten
prompts, preserving `{text}` and the single-word final-line contract.

**Config (`--config` JSON):**

| Key | Default | Meaning |
|-----|---------|---------|
| `optimizer_model` | `gpt-4.1-mini` | Model that rewrites the prompt (NOT the locked task model) |
| `max_failures` | 8 | TRAIN failures to summarize into the rewrite request |

**Run:**
```bash
python .claude/skills/prompt-tuning/scripts/system_refinement.py \
  --project projects/<slug> --train projects/<slug>/data/train.jsonl \
  --prompts projects/<slug>/src/prompts --out projects/<slug>/src/prompts \
  --config '{"optimizer_model":"gpt-4.1-mini","max_failures":8}' --seed 42
```

Rewrites `system.txt` + `task.txt` + `optimize_report.json`.

**Notes:** task model stays locked; only the rewrite uses `optimizer_model`. Script asserts
`{text}` survives. TRAIN only.
