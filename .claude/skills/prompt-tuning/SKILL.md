---
name: prompt-tuning
description: Use when investigating an EPOCH prompt_tune round to choose a prompt-optimization method — few-shot, chain-of-thought, system-refinement, DSPy, or GEPA — from the observed TRAIN failures. Routes to the matching method skill; the investigator picks the method as the round's hypothesis and the executor runs it.
---

# Prompt Tuning (Router)

Pick the prompt-optimization method for this round. This skill is a **router**: it does not
edit prompts itself. The investigator diagnoses TRAIN failures, chooses ONE method here (the
round's hypothesis), and the executor runs that method's optimizer.

> Deep round workflow: `skills/epoch/references/prompt_tune.md`. Method implementations live
> in the per-method skills below.

## Split Discipline

- **TRAIN split only** for selection and optimization. Never read `eval.jsonl`.
- Optimizers that need a validation signal split TRAIN internally — they must not touch EVAL.

## Methods

Each method has a doc under `methods/` and a runner under `scripts/`.

| Method | Doc | Script | Best when | Cost |
|--------|-----|--------|-----------|------|
| Few-shot | `methods/few-shot.md` | `scripts/few_shot.py` | Model understands the task but needs concrete examples; format drift | ~0–K calls |
| Chain-of-thought | `methods/chain-of-thought.md` | `scripts/chain_of_thought.py` | Failures need multi-step reasoning (negation, contrast, comparison) | 0 |
| System refinement | `methods/system-refinement.md` | `scripts/system_refinement.py` | Instructions are vague/ambiguous; a targeted rewrite would help | a few calls |
| DSPy | `methods/dspy.md` | `scripts/dspy_optimize.py` | Automatic joint instruction + few-shot optimization, larger budget | high (100s) |
| GEPA | `methods/gepa.md` | `scripts/gepa_optimize.py` | Hard task, reflective evolution from failure traces; highest ceiling | high (100s) |

## Selection Guide (investigator)

```
Start cheap, escalate only if cheaper methods stall.

Round budget small / first optimization round?
  → pt-chain-of-thought (if reasoning failures) or pt-few-shot (if example-shaped failures)
Instructions themselves unclear or contradictory?
  → pt-system-refinement
Cheaper methods plateaued AND budget available?
  → pt-dspy (joint instruction+demo search)
DSPy plateaued OR task needs trace-level reflection?
  → pt-gepa
```

Escalation order by cost/power: **CoT / few-shot → system-refinement → DSPy → GEPA**.
One method per round (one hypothesis). On a retry, pick a *different* method or config than
the rejected attempt.

## Shared Optimizer Contract

Every method script under `scripts/` takes the SAME interface, so the executor runs any
method identically (only the script name changes):

```bash
python .claude/skills/prompt-tuning/scripts/<method>.py \
  --project projects/<slug> \
  --train   projects/<slug>/data/train.jsonl \
  --prompts projects/<slug>/src/prompts \
  --out     projects/<slug>/src/prompts \
  --config  '<method-specific JSON>' \
  --seed    42
```

**Contract rules (all methods MUST honor):**
1. **TRAIN-only input.** Read `--train` and current `--prompts`. Never open `eval.jsonl`.
2. **Output prompt files** into `--out`: rewrite `system.txt` / `task.txt` and/or write
   `examples.txt` (few-shot demos). `task.txt` keeps the `{text}` placeholder.
3. **Parsing invariant.** The emitted prompt MUST keep the project's output contract — for
   classification, the final line is a single label word — so `evaluate.py` still parses.
4. **Report.** Write `optimize_report.json` to the run dir (or `--out`) with: `method`,
   `config`, `n_demos`, `n_llm_calls`, `internal_train_score`, `notes`.
5. **Determinism.** Honor `--seed` where the method supports it.
6. **Model lock.** The *task* model stays as configured (`llm.model`). DSPy/GEPA may use a
   separate `optimizer_model` / `reflection_model` for the search only — never to answer EVAL.

`evaluate.py` must prepend `examples.txt` to the task prompt when the file exists (few-shot /
DSPy demos). The `create-project` template wires this.

## Common Mistakes

- Picking two methods in one round — one hypothesis, or attribution breaks.
- Letting an optimizer read EVAL for its validation signal — split TRAIN instead.
- Emitting a prompt whose output no longer ends in a single label word — breaks the parser.
