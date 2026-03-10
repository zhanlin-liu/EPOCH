# EPOCH

Multi-round optimization framework powered by a single Claude Code skill.

## What This Is

EPOCH is a `.claude/skills/epoch/` skill that runs iterative optimize-evaluate loops. Given an `epoch_run.yaml` config, it dispatches to the right workflow, investigates failures, implements fixes, evaluates results, and accepts or rejects with evidence — round by round.

## Repository Structure

```
.claude/skills/epoch/
├── SKILL.md                    # Entry point — dispatches by task_type
├── agents/                     # Role definitions (orchestrator, investigator, executor, reviewer, etc.)
└── references/                 # Task-type workflows
    ├── prompt_tune.md          # Optimize LLM prompts
    ├── finetune.md             # Tune ML hyperparameters
    ├── rule_based.md           # Optimize rule-based systems
    ├── code_improvement.md     # Fix bugs, optimize performance
    └── create_skill.md         # Generate custom task-type references
projects/                       # Project configs (epoch_run.yaml per project)
```

## How It Works

1. User creates an `epoch_run.yaml` with `task_type` and evaluation config
2. User invokes `/epoch` or says "epoch"
3. SKILL.md reads the config and loads the matching reference + agents
4. Round 1: Establish baseline (seed planner → baseline executor)
5. Rounds 2+: Investigate → implement → evaluate → accept/reject
6. Unknown `task_type`: `create_skill.md` interviews the user and generates a new reference

## Supported Task Types

| task_type | Reference | What It Optimizes |
|-----------|-----------|-------------------|
| `prompt_tune` | `references/prompt_tune.md` | LLM prompt text |
| `finetune` | `references/finetune.md` | ML hyperparameters |
| `rule_based` | `references/rule_based.md` | Rule conditions/thresholds |
| `code_improvement` | `references/code_improvement.md` | Algorithm correctness & performance |

## Conventions

- **Branch naming**: `epoch/<project_slug>/<run_id>/round-<N>`
- **Run ID format**: `run-YYYYMMDD-HHMM`
- **Config file**: `projects/<slug>_run.yaml` (sibling to task folder)
- **TRAIN/EVAL split**: ML tasks use separate splits to prevent overfitting; code_improvement uses all tests
- **Evidence-based decisions**: Every accept/reject requires metrics tables and rationale

## Git Workflow

- `main` — stable merged results
- `develop` — integration branch
- `epoch/<slug>/<run-id>/round-<N>` — per-round optimization branches