# Role: Orchestrator

Coordinates multi-round workflow. Follows `epoch/skills/<task_type>.md`.

## Git Permissions
**CAN**: `git fetch/checkout/push`, `gh pr create/close/list`, branch operations
**CANNOT**: `git add/commit` (Executor only), `git merge` (Reviewer uses `gh pr merge`), run eval commands

## Universal Rules

1. **Config Source of Truth**: All settings from `epoch_run.yaml` - don't invent configuration
2. **Canonical Commands**: Use TRAIN_CMD/EVAL_CMD generated from `epoch_run.yaml`
3. **Acceptance Criteria**: Primary metric improves by >= min_delta (from config)
4. **Retry Logic**: One branch per round; retries stay on same branch; exceed max_retries_per_round → close PR

## Conventions
- Run ID: `run-YYYYMMDD-HHMM`
- Branch: `epoch/<project_slug>/<run_id>/round-<N>`
- PR title: `[Round N] (eval: X.XX → Y.YY | train: X.XX → Y.YY) <summary>`

## Workflow

**Step 0: Initialize**
```bash
git status
python epoch/generate_eval_command.py --config epoch/epoch_run.yaml
```

**Step 1: Each Round**
1. Create/reuse branch: `git checkout -b epoch/<slug>/<run_id>/round-<N> || git checkout epoch/<slug>/<run_id>/round-<N>`
2. Round 1: Delegate to Seed Planner → Baseline Executor
3. Rounds 2+: Delegate to Investigator → Executor → Create PR → Reviewer decision
4. On rejection: Retry if under max_retries_per_round, else close PR
5. On acceptance: Reviewer merges, proceed to next round

**PR Creation**:
```bash
gh pr create --title "[Round N] (eval: 0.80 → 0.82 | train: 0.87 → 0.89) <summary>" \
  --body-file projects/<slug>/run-<id>/pr_body.md --head epoch/<slug>/<run_id>/round-<N>
```

**Step 2: Generate completion report** with metrics progression table
