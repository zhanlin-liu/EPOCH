---
name: code-improvement
description: Use when investigating an EPOCH code_improvement round — running the test suite to localize a failing test or performance bottleneck, then proposing one targeted code fix with rationale. All tests are visible (no TRAIN/EVAL split).
---

# Code Improvement

Localize a bug or bottleneck from the test suite and propose one fix. The investigator's
technique for `code_improvement` rounds.

> Deep round workflow: see `skills/epoch/references/code_improvement.md`. This skill is the
> investigator's hands-on diagnosis technique within that workflow.

## When to Use

- The investigator is analyzing a `code_improvement` round.
- You have a failing test or a slow path and need to pinpoint one fix.

## Data Access

- **All tests visible** — code_improvement has no TRAIN/EVAL split. Use the full suite.

## Diagnosis → Fix

| Symptom | Approach | Typical change |
|---------|----------|----------------|
| One test fails | Read the assertion + trace to source | Fix the specific logic path |
| Many tests fail similarly | Shared root cause | Fix the common helper/contract |
| Test passes but slow | Profile the hot path | Optimize the one bottleneck |
| Flaky test | Find the nondeterminism | Make the path deterministic |

## Process

1. Run `scripts/failing_tests.sh "<test_cmd>"` to list failures.
2. Trace the dominant failure (or bottleneck) to its source.
3. Propose **one** targeted fix, with rationale tying fix → failure.

## Scripts

- `scripts/failing_tests.sh` — run the project's test command and surface the failures.
  ```bash
  bash scripts/failing_tests.sh "pytest projects/<slug>/tests/"
  ```

## Common Mistakes

- Fixing several unrelated failures in one round — split them so each delta is attributable.
- Optimizing before profiling — confirm the bottleneck with measurement first.
