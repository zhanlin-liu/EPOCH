---
name: epoch
description: >
  Multi-round optimization loop for improving prompts, rules, hyperparameters, and code
  through evidence-based iteration. Use this skill when the user mentions "epoch" or
  invokes /epoch. Reads a epoch_run.yaml config to determine task type and dispatches
  to the appropriate workflow.
---

# EPOCH: Multi-Round Optimization

EPOCH runs an iterative optimization loop: Investigate failures, implement a fix, evaluate the result, accept or reject with evidence, repeat.

## When to Use

- User says "epoch", "run epoch", or uses `/epoch`
- User has a `epoch_run.yaml` config file
- User describes an optimization task in conversation

## Quick Start

**Config provided** (e.g. `/epoch projects/wine_run.yaml`):
1. Read the project's `epoch_run.yaml`
2. If `env` is configured, ensure the environment is set up (e.g. `uv sync` in `env.path`). Wrap all commands (`evaluation.cmd`, `evaluation.test_cmd`, `evaluation.train_cmd`/`evaluation.eval_cmd`) with the env manager (e.g. `uv run --project <env.path> <cmd>`)
3. Identify `task_type` from config
4. Load the matching reference and active agents
5. Execute the workflow

**No config** (e.g. `/epoch` or "epoch, classify wine cultivars"):
1. Load `references/create_project.md`
2. Interview the user (3-5 questions max)
3. Generate `projects/<slug>_run.yaml` + scaffold project files using ONLY the templates in `create_project.md` — do NOT read or reference other project folders, and do NOT check git log or git history
4. Validate the scaffold runs
5. Confirm with user, then proceed with the generated config

---

## Dispatch

Read `epoch_run.yaml` and dispatch based on `run.task_type`:

| task_type | Reference to Load | Description |
|-----------|------------------|-------------|
| `prompt_tune` | `references/prompt_tune.md` | Optimize LLM prompts |
| `finetune` | `references/finetune.md` | Tune ML hyperparameters |
| `rule_based` | `references/rule_based.md` | Optimize rule-based systems |
| `code_improvement` | `references/code_improvement.md` | Fix bugs, optimize performance |

If no config is provided, load `references/create_project.md` to interview the user and scaffold the project.

If `task_type` is not recognized, load `references/create_skill.md` to generate a new task-type reference.

---

## Agents

Agents define role behavior, permissions, and constraints. Load them as needed during the workflow.

| Agent | When to Load | Purpose |
|-------|-------------|---------|
| `agents/orchestrator.md` | Always | Coordinates rounds, manages branches and PRs |
| `agents/seed_planner.md` | Round 1 | Designs baseline evaluation approach |
| `agents/baseline_executor.md` | Round 1 | Implements evaluation infrastructure |
| `agents/investigator.md` | Rounds 2+ | Analyzes failures, proposes changes |
| `agents/executor.md` | Rounds 2+ | Implements changes, commits |
| `agents/reviewer.md` | Rounds 2+ | Evaluates results, accepts/rejects |

Users may add custom agents or exclude agents from this list based on their needs.

---

## Shared Conventions

These apply across all task types.

### Run ID and Branching

- **Run ID**: `run-YYYYMMDD-HHMM`
- **Branch**: `epoch/<project_slug>/<run_id>/round-<N>`
- One branch per round. Retries stay on the same branch.

### Project Output Directory

Config and task files are organized as:

```
projects/
├── <slug>_run.yaml            # epoch config (sibling to task folder)
└── <slug>/                    # task folder
    ├── evaluate.py            # ML tasks: train/eval metric runner
    ├── tests/                 # code_improvement: test suite
    ├── rules/                 # or other task-specific files
    └── <run_id>/              # run artifacts
        ├── baseline_metrics.json
        ├── proposed_metrics.json
        ├── delta_round_N.json
        ├── pr_body.md
        └── run_summary.md
```

Never write outputs to the repository root.

### PR Format

- Round 1: `[Round 1] (Baseline: <metric>=<value>) Initial <artifact>`
- Round 2+: `[Round N] (<metric>: <old> -> <new>) <brief summary>`

### Acceptance Criteria

A round is accepted when:
1. Primary metric improves >= `min_delta` (from config)
2. No constraint violations (task-specific)
3. Evidence is provided (metrics table + rationale)

### Rejection Requirements

Every rejection must include:
1. **Metrics table** with baseline, proposed, delta, threshold, status
2. **Root cause** — why the change didn't work
3. **Retry recommendation** — what to try differently

No subjective rejections. "Doesn't seem right" is not valid.

### Retry Protocol

When a round is rejected and retries remain:
1. Read the rejection evidence (PR comments)
2. Analyze what failed and why
3. Choose strategy:
   - **REFINE**: Small regression + right direction — adjust magnitude
   - **REVERT**: Large regression + wrong direction — try different approach
4. Propose a different change than the previous attempt

### TRAIN/EVAL Separation

For ML tasks (prompt_tune, finetune, rule_based):
- **Investigation**: TRAIN split only — never inspect EVAL data
- **Evaluation**: EVAL split only — metrics computed here
- This prevents overfitting to the evaluation set

For code_improvement: All tests are visible (no split).

---

## Workflow Overview

### Phase 1: Baseline (Round 1)

1. Read `agents/seed_planner.md` — design evaluation approach
2. Read `agents/baseline_executor.md` — implement and run baseline
3. Save `baseline_metrics.json`
4. Create branch, commit, push, open PR

### Phase 2: Optimization (Rounds 2+)

For each round:

1. **Branch setup**: Create or reuse branch
2. **Investigate**: Read `agents/investigator.md` + task reference — analyze failures on TRAIN, propose changes
3. **Implement**: Read `agents/executor.md` — apply changes, commit, push
4. **Evaluate**: Read `agents/reviewer.md` — run EVAL, compare metrics, decide accept/reject
5. **Handle decision**:
   - Accept: Merge PR, proceed to next round
   - Reject + retries left: Retry on same branch
   - Reject + no retries: Close PR, proceed to next round

### Completion

After all rounds, generate a run summary with the full metrics progression.

---

## Configuration

Each project needs a `epoch_run.yaml`. The config structure differs by task type:

**ML tasks** (prompt_tune, finetune, rule_based) use `evaluation:` with train/eval split:

```yaml
project:
  name: "Project Name"
  slug: "project_slug"

run:
  task_type: "rule_based"   # prompt_tune | finetune | rule_based
  max_rounds: 10
  max_retries_per_round: 2

env:
  manager: uv
  path: "projects/<slug>"

evaluation:
  primary_metric: "precision"
  min_delta: 0.01
  deterministic: true
  train_cmd: "python projects/<slug>/evaluate.py train"
  eval_cmd: "python projects/<slug>/evaluate.py eval"

git:
  push_to_remote: true
  create_prs: true
  target_branch: "develop"
```

**Code improvement** uses `evaluation:` with `cmd` (the program under test) and `test_cmd` (the test runner):

```yaml
project:
  name: "Project Name"
  slug: "project_slug"

run:
  task_type: "code_improvement"
  max_rounds: 5
  max_retries_per_round: 1

env:
  manager: uv
  path: "projects/<slug>"

evaluation:
  primary_metric: "execution_time"
  min_delta: 0.05
  deterministic: true
  cmd: "python projects/<slug>/main.py"
  test_cmd: "pytest projects/<slug>/tests/"

git:
  push_to_remote: true
  create_prs: true
  target_branch: "develop"
```

Task-specific config sections (`llm:`, `ml:`, `rules:`) are documented in the corresponding reference file.

---

## Discipline

1. **No git archaeology during project creation** — when creating a new project or generating a config yaml, do NOT run `git log`, `git show`, or any git history commands to look at past runs or projects. Start fresh from the templates and the user's input only.
2. One hypothesis per round — clear attribution of what caused the change
3. No scope creep — only modify what the investigation identified
4. Always re-run evaluation — never assume improvement
5. Every rejection must change strategy — no repeating the same approach
6. Small change, measure, decide, repeat
7. **Project isolation** — only read/modify files within `projects/<slug>/` and `projects/<slug>_run.yaml`. Never scan, read, or reference other project folders — not even to "check patterns" or "follow conventions". Each project is scaffolded from the templates in `create_project.md`, not copied from siblings.
