---
name: github
description: Use when performing any git or GitHub operation in an EPOCH run — creating or reusing per-round branches, committing and pushing changes, opening/merging/closing PRs, or formatting PR titles and bodies to EPOCH conventions.
---

# GitHub

Git and GitHub operations for EPOCH rounds, with the conventions baked in so branches, PR
titles, and commits stay consistent across a run.

## When to Use

- Creating or reusing a round branch.
- Committing and pushing a round's changes.
- Opening, merging, or closing a round PR.
- Formatting a PR title/body from round metrics.

Who uses which part (the orchestrator points each agent to its slice):
- **Orchestrator** → branches, `gh pr create/merge/close`.
- **Executor** → `git add/commit/push` only.

## Conventions

- **Run ID**: `run-YYYYMMDD-HHMM`
- **Branch**: `epoch/<project_slug>/<run_id>/round-<N>` — one branch per round; retries reuse it.
- **PR title**: `[Round N] (eval: X.XX → Y.YY | train: X.XX → Y.YY) <summary>`
- **Commit**: `Round N: <summary>` + bullets + `Based on investigation: <rationale>`

## Quick Reference

| Operation | Command |
|-----------|---------|
| Create/reuse branch | `git checkout -b <branch> \|\| git checkout <branch>` |
| Commit | `git add -A && git commit -m "Round N: ..."` |
| Push | `git push -u origin <branch>` |
| Open PR | `gh pr create --title "..." --body-file <pr_body.md> --head <branch>` |
| Merge | `gh pr merge --squash` |
| Close (rejected, no retries) | `gh pr close <branch>` |

## Scripts

- `scripts/pr_title.py` — build an EPOCH PR title from metric values.
  ```bash
  python scripts/pr_title.py --round 3 \
    --eval-old 0.80 --eval-new 0.82 --train-old 0.87 --train-new 0.89 \
    --summary "Tighten threshold on rule R2"
  ```

## Common Mistakes

- Committing from the orchestrator — only the executor commits.
- Opening a new branch on a retry — retries stay on the same round branch.
- Hand-formatting PR titles — use `scripts/pr_title.py` so the format never drifts.
