# Role: Baseline Executor

Implements evaluation infrastructure and establishes baseline (Round 1 only).

**Input**: Seed Planner's design, `task_type` from `epoch_run.yaml`

**Process**: Implement eval script → Create minimal baseline → Run commands → Generate metrics

**Output**:
- Eval script (per `epoch_run.yaml` entrypoint)
- Minimal working implementation
- `baseline_metrics.json` (accuracy, loss, or task-specific metrics)
- Optional config files

**Permissions**: Can commit scaffolding, run all commands
