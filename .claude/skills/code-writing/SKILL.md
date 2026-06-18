---
name: code-writing
description: Use when implementing a change specified by an EPOCH investigation report — applying exactly the proposed edit within a bounded scope, with no opportunistic refactors, so the resulting metric delta is attributable to one hypothesis.
---

# Code Writing

Implement the one change an investigation report specifies — and nothing else. In EPOCH,
scope discipline is what keeps a round's metric change traceable to a single cause.

## When to Use

- The executor is applying an investigation report's proposed change.
- Round 1: building the minimal baseline implementation from a design doc.

## Core Principle

**One hypothesis per round.** The report names the change; you make that change. Anything
you touch beyond it pollutes attribution — if the metric moves, you can no longer say why.

## Quick Reference

| Do | Don't |
|----|-------|
| Implement exactly what the report specifies | Fix unrelated bugs "while I'm here" |
| Keep edits minimal and local | Rename, reformat, or restructure adjacent code |
| Match surrounding style and idioms | Introduce a new dependency unless the report calls for it |
| Verify the change applies cleanly | Run EVAL commands (that's the evaluator) |

## Process

1. Read the investigation report; identify the single change.
2. Make that change, matching local style.
3. Confirm scope: run `scripts/scope_check.sh` and confirm the diff touches only what the report named.
4. Hand off to the executor's commit step (see the `github` skill).

## Scripts

- `scripts/scope_check.sh` — print a diff stat of the working tree so you can confirm the
  change stayed within the intended files before committing.
  ```bash
  bash scripts/scope_check.sh
  ```

## Common Mistakes

- Bundling a second improvement into the round — split it into its own round.
- Reformatting a whole file the change only touched in one spot — inflates the diff and hides the real edit.
- "Improving" code the report didn't mention — out of scope by definition.
