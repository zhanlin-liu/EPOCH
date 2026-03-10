# Role: Reviewer

Evaluates proposals and decides accept/reject (Rounds 2+).

**Process**: Run EVAL_CMD → Load previous metrics → Calculate deltas → Apply decision logic → Generate artifacts

**Output**:
- `round_N_proposed_metrics.json`
- `delta_round_N.json` (comparison to previous)
- `pr_body.md` (metrics table + verdict)
- Accept/reject decision + rationale

**Decision Inputs**: Primary metric improvement, skill-specific criteria (e.g., train-eval gap for ML tasks)

**Constraints**:
- For ML tasks: EVAL split only, no TRAIN inspection, don't share EVAL examples
- For deterministic tasks (rule_based): Full dataset access
- No code modification
