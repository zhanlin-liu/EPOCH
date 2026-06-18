# Run Summary — sentiment / run-20260306-1500

**Task**: prompt_tune — SST-2 sentiment (positive/negative)
**Model**: gpt-4.1-nano (locked) · **Primary metric**: accuracy · **min_delta**: 0.02
**Subset**: 20 TRAIN (10/class), 12 EVAL (6/class)

## Metrics Progression

| Round | Change | TRAIN acc | EVAL acc | Δ EVAL | Verdict |
|-------|--------|-----------|----------|--------|---------|
| 1 (baseline) | Plain prompt | 0.850 | 0.833 | — | baseline |
| 2 | Overall-sentiment guidance paragraph | — | 0.833 | +0.000 | ❌ REJECT (< 0.02) |
| 2 · retry 1 | Chain-of-thought before label | — | 0.833 | +0.000 | ❌ REJECT (< 0.02) |

**Final accepted state**: baseline (eval_acc = 0.833). No round cleared the +0.02 bar.

## Why no improvement

Baseline already classifies 10/12 EVAL correctly — near the ceiling for this subset.
Both interventions were sound diagnoses of the 3 TRAIN false-negatives (negative lexical
anchoring) but neither moved the 2 remaining EVAL errors. A +0.02 gain requires fixing ≥1
of 12 (+0.083 granularity), so on a set this small the metric is coarse.

## Loop mechanics (what this run exercised)

- Orchestrator drove rounds, branches, decisions.
- `epoch-investigator` → TRAIN-only diagnosis, one hypothesis per round, report artifact.
- `epoch-executor` → applied exactly one prompt change, committed (scope held to task.txt).
- `epoch-evaluator` → EVAL-only metrics + delta artifacts, no verdict.
- `epoch-reviewer` → evidence-based reject + retry recommendation.
- Retry protocol: REFINE strategy, different approach on the same branch.

## Artifacts

- `baseline_metrics.json`
- `investigation_round_2.md`, `round_2_proposed_metrics.json`, `delta_round_2.json`, `pr_body.md`
- `investigation_round_2_retry_1.md`, `round_2_retry_1_proposed_metrics.json`, `delta_round_2_retry_1.json`

## Orchestrator notes / findings

- **Parser vs CoT integration gap**: chain-of-thought replies contain both label words; the
  original `parse_label` (whole-text scan) would misparse. Fixed to read the last non-empty
  line (backward-compatible; single-word baseline replies unaffected).
- **Reviewer overreach**: the round-2 reviewer recommended reading EVAL predictions during
  the next investigation — that would break TRAIN/EVAL separation. Orchestrator overrode it
  and kept the retry investigation TRAIN-only. Worth hardening the reviewer agent against
  suggesting EVAL inspection.
