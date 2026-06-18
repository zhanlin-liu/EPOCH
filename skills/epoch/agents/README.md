# EPOCH Agents

EPOCH runs each optimization round as a relay of five specialized agents. Each agent
owns one stage of the loop — **coordinate → investigate → implement → evaluate → judge** —
and hands a written artifact to the next. The separation is deliberate: it keeps every
metric change attributable to exactly one hypothesis, and it keeps the agent that *renders
the verdict* from being the one that *generated the numbers*.

```
                        ┌──────────────┐
                        │ Orchestrator │  owns branches, PRs, round flow
                        └──────┬───────┘
          delegates each round │
   ┌───────────────┬──────────┴────┬───────────────┬──────────────┐
   ▼               ▼               ▼               ▼              ▼
Investigator → Executor   →    Evaluator   →   Reviewer   →  (next round)
 diagnose &     apply the       run EVAL,        accept /
 propose        change          produce metrics  reject
```

Round 1 is the same relay in "baseline" mode: the investigator designs the evaluation
approach and the executor builds it, producing the baseline metrics the rest of the run
measures against.

| Agent | File | Loaded | One-line role |
|-------|------|--------|---------------|
| Orchestrator | [orchestrator.md](orchestrator.md) | Always | Coordinates rounds; owns branches, PRs, merges |
| Investigator | [investigator.md](investigator.md) | Every round | Diagnoses failures, proposes one change |
| Executor | [executor.md](executor.md) | Every round | Applies the change, commits |
| Evaluator | [evaluator.md](evaluator.md) | Every round | Runs EVAL, produces metrics and deltas |
| Reviewer | [reviewer.md](reviewer.md) | Every round | Accepts or rejects on the evidence |

---

## Orchestrator

**Coordinates the multi-round workflow.** The only agent that touches branch and PR state.

- **Owns**: project creation (no-config bootstrap), branch creation/reuse, `gh pr create/close/merge`, round sequencing, retry logic.
- **Cannot**: `git add/commit` (executor's job), run EVAL (evaluator's job), decide accept/reject (reviewer's job).
- **Input**: `epoch_run.yaml` — or, when none is provided, the user's task description.
- **Output**: per-round branches, PRs, and the final run-summary report.

When invoked with no config (`/epoch` alone, or a task described in conversation), the
orchestrator runs **Phase 0** first: it loads the `create-project` skill to interview the
user, scaffold `epoch_run.yaml` + the project, and validate it — then proceeds into the loop.
Otherwise it never does the substantive work of a round — it delegates each stage and acts
on the reviewer's decision (merge on accept, retry or close on reject).

## Investigator

**Diagnoses and proposes — never implements.** This is where the round's single hypothesis
is formed.

- **Process**: sample data → analyze failures → identify the pattern → propose *one* change with rationale.
- **Output**: an investigation report (the attribution record for the round).
- **Round 1 (baseline mode)**: instead of diagnosing failures, designs the evaluation approach and minimal baseline strategy.
- **Constraints**: ML tasks → TRAIN split only, never inspect EVAL. No code modification, no execution.

Keeping the investigator separate from the executor is what enforces *one hypothesis per
round*: the proposed change is written down before any code is touched.

## Executor

**Applies the proposed change and commits — nothing more.** Implements exactly what the
investigation report specifies; no opportunistic "while I'm in here" edits.

- **Process**: read the investigation report → make the change → commit → push.
- **Output**: modified files + a commit that references the investigation rationale.
- **Round 1 (baseline mode)**: builds the evaluation infrastructure and produces `baseline_metrics.json`.
- **Git**: `git add/commit/push` only — no `checkout`, `merge`, or `pr create`.
- **Constraints**: implementation only; ML tasks → no EVAL commands. Scope is bounded by the report.

## Evaluator

**Produces the numbers — and only the numbers.** Runs the evaluation and computes deltas,
but renders no verdict. Splitting measurement from judgment keeps the reviewer honest.

- **Process**: run `EVAL_CMD` → load previous metrics → compute deltas.
- **Output**: `round_N_proposed_metrics.json`, `delta_round_N.json`.
- **Constraints**: ML tasks → EVAL split only, never inspect or leak EVAL examples; deterministic tasks (rule_based) may use the full dataset. No code modification, no accept/reject call.

## Reviewer

**Decides accept or reject, on the evidence the evaluator produced.** Does not run the
metrics itself, so the verdict is rendered against numbers it did not generate.

- **Decision inputs**: primary-metric improvement vs. `min_delta`, plus task-specific criteria (e.g. train/eval gap for ML tasks).
- **Output**: `pr_body.md` (metrics table + verdict) and the accept/reject decision with rationale.
- **Discipline**: no subjective rejections. Every rejection includes a metrics table, a root cause, and a retry recommendation.
- **Constraints**: no code modification; reads metrics, does not regenerate them.

---

## Why five, and why split this way

- **Investigator ≠ Executor** — forces a written hypothesis before code changes, so every metric delta is attributable to one cause. Merging them invites scope creep, the failure mode EPOCH exists to prevent.
- **Evaluator ≠ Reviewer** — the agent that generates the metrics is not the agent that judges them. Cleaner evidence trail on rejected rounds.
- **Baseline folded into the round agents** — round 1 is just "baseline mode" of the investigator and executor, not two extra roles. Fewer files to keep in sync.

Users may add custom agents or drop agents from this set based on their needs.
