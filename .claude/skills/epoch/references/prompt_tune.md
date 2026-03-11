# Skill: Prompt Tuning

**Goal**: Optimize LLM prompt performance to improve evaluation accuracy

**Optimization Target**: Evaluation accuracy on EVAL split

**Version**: Single-agent optimized (all workflows inlined)

---

## Overview

This skill optimizes LLM prompts through iterative refinement while preventing EVAL leakage. The LLM model is locked—only prompt text can be modified.

**Key Principles:**
- ✅ Investigate failures on TRAIN split only
- ✅ Evaluate improvements on EVAL split only
- ❌ Never use EVAL examples in prompts
- ❌ Never inspect EVAL during investigation

---

## Orchestrator: Multi-Round Coordination

### Universal Rules

1. **Config source of truth**: All settings from `epoch_run.yaml`
2. **Canonical commands**: Use TRAIN_CMD/EVAL_CMD from config
3. **Acceptance criteria**: eval_accuracy improves by >= min_delta, no EVAL leakage
4. **Retry logic**: One branch per round; retries on same branch; exceed max → close PR

### Conventions

**Run ID**: `run-YYYYMMDD-HHMM`
**Branch**: `epoch/<project_slug>/<run_id>/round-<N>`

**PR Titles:**
- Round 1: `[Round 1] (Baseline: eval_acc=0.76) Initial prompt`
- Round 2+: `[Round N] (eval_acc: 0.76 → 0.82) Add negation handling`

### Workflow Steps

**For Each Round (1 to N):**

1. **Create/reuse branch:**
   ```bash
   git checkout -b epoch/<slug>/<run_id>/round-<N> || git checkout epoch/<slug>/<run_id>/round-<N>
   if [ "$PUSH_TO_REMOTE" = "true" ]; then
     git push -u origin epoch/<slug>/<run_id>/round-<N> || true
   fi
   ```

2. **Round 1 Only**: Baseline establishment (see Phase 1 below)

3. **Rounds 2+**: Optimization loop
   - Investigation (TRAIN only)
   - Implementation (modify prompts)
   - Evaluation (EVAL only)
   - Decision (accept/reject with evidence)

4. **Handle decision:**
   - Accept: Merge PR (if enabled), proceed to next round
   - Reject: Retry if count < max, else close PR and proceed

5. **After all rounds**: Generate run summary with metrics progression

---

## Phase 1: Baseline Establishment (Round 1)

### Seed Planner (Design)

**Task**: Design evaluation approach and prompt template

**IMPORTANT**: The baseline prompt must NOT use information from the `tune` section of `epoch_run.yaml`. The `tune` section (e.g., strategy, techniques) is reserved for Rounds 2+. The baseline should be a plain, generic prompt so it serves as a true unoptimized starting point.

**Deliverables:**
1. Evaluation script interface:
   - Input: data split, prompt template
   - Output: metrics JSON (train_accuracy, train_loss, eval_accuracy, eval_loss)

2. Prompt template structure:
   - System instructions
   - Task description
   - Output format specification

3. Baseline prompt:
   - Generic task instructions (derived from `run.goal` and `data` config only)
   - Minimal, straightforward instructions — no advanced techniques
   - Clear format requirements
   - Do NOT add few-shot examples, chain-of-thought, or other strategies from `tune`

### Baseline Executor (Implementation)

**Task**: Implement evaluation and establish baseline

**IMPORTANT**: Do NOT reference the `tune` section when building the baseline. The baseline must reflect a plain, unoptimized prompt.

**Steps:**
1. Create evaluation script
2. Create prompt files in `projects/<slug>/src/prompts/`:
   - `system.txt` - System instructions
   - `task.txt` - Task description
3. Implement LLM inference (uses llm.model from config)
4. Run TRAIN_CMD to verify
5. Run EVAL_CMD to establish baseline
6. Save baseline_metrics.json

---

## Phase 2: Multi-Round Optimization (Rounds 2+)

### Investigation (TRAIN Only)

**Task**: Analyze TRAIN failures and propose improvements

**Process:**
1. Run evaluation on TRAIN split
2. Sample N failures (investigation.samples from config)
3. Analyze patterns for M iterations (investigation.rounds)
4. Identify failure types:
   - **Negation handling**: "not", "never", "no" ignored
   - **Edge cases**: Empty inputs, boundaries
   - **Comparisons**: Element comparison failures
   - **Ambiguity**: Vague instructions
   - **Format errors**: Output format violations
5. Propose specific prompt modifications

**Retry Detection:**
```bash
git branch -r | grep "round-N"  # Exists → Retry
```

**If Retry:**
1. Read rejection evidence: `gh pr view <PR> --comments`
2. Analyze what failed and why
3. Apply retry strategy:
   - Small regression + right pattern → REFINE (adjust values)
   - Large regression + wrong pattern → REVERT (pivot)
4. Propose DIFFERENT approach

**Investigation Report:**
```markdown
## Investigation Report - Round N {(RETRY {count})}

**Samples Analyzed**: {investigation.samples} (from TRAIN)
**Investigation Rounds**: {investigation.rounds}

{If retry:}
### Previous Attempt
- What tried: ...
- Why failed: ...
- What NOT to try: ...
- New approach: ...

### Current Performance (TRAIN)
- Train accuracy: {value}

### Failure Pattern Analysis

**Pattern 1: {Name}** ({count} samples, {percent}%)
- Description: ...
- Examples:
  - Input: "{input}" → Expected: "{exp}" → Got: "{actual}"
- Root cause: ...

**Pattern 2: {Name}** ({count} samples, {percent}%)
...

### Proposed Changes

**Change 1: {Title}**
- File: projects/<slug>/src/prompts/{file}.txt
- Current: {quote}
- Proposed: {quote}
- Rationale: Addresses Pattern X

### Expected Impact
- Train accuracy: {current} → {expected}
```

**Constraints:**
- ✅ TRAIN split only - no EVAL inspection
- ❌ No EVAL examples in proposals

---

### Implementation

**Task**: Modify prompt files and commit

**Process:**
1. Read investigation report
2. Apply changes to prompt files:
   - `projects/<slug>/src/prompts/system.txt`
   - `projects/<slug>/src/prompts/task.txt`
   - `projects/<slug>/src/prompts/examples.txt`
3. Verify no EVAL examples used
4. Run TRAIN_CMD (optional verification)
5. Commit and push

**Allowed:**
- ✅ Prompt wording (clarity, specificity)
- ✅ System instructions
- ✅ Few-shot examples FROM TRAIN ONLY
- ✅ Output format specification

**Forbidden:**
- ❌ EVAL examples
- ❌ EVAL-specific instructions
- ❌ Changing llm.model

**Commit Format:**
```
Round N{, Retry M}: {Brief summary}

- Modified {file}: {change}
- Modified {file}: {change}

Based on investigation: {brief findings}
```

---

### Evaluation (EVAL Only)

**Task**: Evaluate on EVAL and decide with evidence

**Process:**
1. Run EVAL_CMD (non-deterministic, must re-run)
2. Load baseline metrics
3. Calculate deltas
4. Check EVAL leakage (review prompt files)
5. Apply decision logic
6. Generate delta_round_N.json and pr_body.md

**Decision Logic:**

**ACCEPT if:**
- eval_accuracy improvement >= min_delta
- AND no EVAL leakage detected
- AND prompt remains general

**REJECT if:**
- eval_accuracy decreases
- OR improvement < min_delta
- OR EVAL leakage detected
- OR prompt overly specific

**CRITICAL: Evidence Required**

Every rejection MUST include:

**1. Metrics table:**
| Metric | Baseline | Proposed | Delta | Threshold | Status |
|--------|----------|----------|-------|-----------|--------|
| eval_accuracy | 0.820 | 0.824 | +0.004 | ≥0.01 | ❌ |

**2. Sample-level evidence:**
- Which samples regressed (indices)
- Pattern description

**3. Root cause:**
- Why metrics changed
- What implementation caused it

**4. Retry recommendation:**
- What NOT to try again
- Suggested different approach

**Invalid rejections:**
- ❌ "Doesn't seem right"
- ❌ "Prompt too complex"

**Valid rejections:**
- ✅ "eval_acc -0.02. Samples 42,89,156 regressed (negation cases). Root cause: line 15 conflicts. Try: Remove line 15, add examples instead."

**Output Files:**

**delta_round_N.json:**
```json
{
  "round": 2,
  "retry_count": 0,
  "baseline_metrics": {"eval_accuracy": 0.76, "train_accuracy": 0.78},
  "proposed_metrics": {"eval_accuracy": 0.82, "train_accuracy": 0.84},
  "deltas": {"eval_accuracy": 0.06, "train_accuracy": 0.06},
  "verdict": "ACCEPT",
  "rationale": "...",
  "eval_leakage_check": "PASS"
}
```

**pr_body.md:**
```markdown
## Round N: Prompt Tuning Results {(RETRY {count})}

### Changes
- Modified system.txt: Add negation emphasis
- Modified examples.txt: Add comparison example

### Metrics

| Metric | Baseline | Proposed | Delta | Threshold | Status |
|--------|----------|----------|-------|-----------|--------|
| eval_accuracy | 0.76 | 0.82 | +0.06 | ≥0.01 | ✅ |
| train_accuracy | 0.78 | 0.84 | +0.06 | - | - |

### EVAL Leakage Check: ✅ PASS

### Verdict: ✅ ACCEPT

**Evidence:**
eval_accuracy improved +0.06 (>= min_delta 0.01)
No EVAL leakage detected
Train-eval gap: 0.02 (good generalization)
```

**On Accept:**
```bash
gh pr review <PR> --approve --body-file pr_body.md
gh pr merge <PR> --squash --delete-branch
```

**On Reject:**
```bash
gh pr review <PR> --request-changes --body-file pr_body.md
# Branch preserved for retry
```

---

## Configuration

From `epoch_run.yaml`:

```yaml
project:
  name: "My Prompt Tuner"
  slug: my_task

run:
  id: run-YYYYMMDD-HHMM
  goal: "Optimize prompt for <task description>"
  task_type: prompt_tune
  max_rounds: 5
  max_retries_per_round: 1

env:
  manager: uv
  path: "projects/<slug>"

llm:
  model: "gpt-4.1-mini"   # Locked during run
  async: true              # Use async API for parallel inference
  concurrency: 12          # Max concurrent requests

tune:
  strategy: ["few shots", "chain of thought"]  # Strategies to try in Rounds 2+

subset:
  enabled: true
  num_classes: 4            # Number of classes to include (use all if omitted)
  train_samples_per_class: 10  # TRAIN samples per class
  eval_samples_per_class: 6   # EVAL samples per class

data:
  source: "sst2"           # Dataset name
  library: "datasets"      # Loading library (datasets, sklearn, csv)

evaluation:
  primary_metric: accuracy
  min_delta: 0.02
  deterministic: false     # Must re-run (LLM non-deterministic)
  train_cmd: "python projects/<slug>/evaluate.py train"
  eval_cmd: "python projects/<slug>/evaluate.py eval"

git:
  push_to_remote: true
  create_prs: true
  target_branch: develop
```

### Config Field Reference

| Section | Field | Description |
|---------|-------|-------------|
| `llm.model` | LLM model to use | Locked — cannot change during optimization |
| `llm.async` | Enable async API | Parallel inference for speed |
| `llm.concurrency` | Max parallel requests | Balance speed vs. rate limits |
| `tune.strategy` | List of strategies | Applied in Rounds 2+ (not baseline). Options: "few shots", "chain of thought", "system prompt refinement" |
| `subset.enabled` | Enable subset mode | Controls per-class sampling |
| `subset.num_classes` | Classes to include | Use all if omitted |
| `subset.train_samples_per_class` | TRAIN samples per class | Used for investigation only |
| `subset.eval_samples_per_class` | EVAL samples per class | Used for evaluation only |
| `data.source` | Dataset identifier | Name for datasets library, path for CSV, etc. |
| `data.library` | How to load data | "datasets" (HuggingFace), "sklearn", "csv" |

---

## Subset Mode

By default, prompt_tune projects use a **subset** of the dataset for fast iteration. The subset config is defined in `epoch_run.yaml`:

```yaml
subset:
  enabled: true
  num_classes: 4
  train_samples_per_class: 10
  eval_samples_per_class: 6
```

When `subset.enabled` is true, create a **separate data prep script** (`projects/<slug>/prepare_data.py`) that:
1. Downloads/loads the full dataset once
2. Selects `num_classes` classes (deterministic selection using seed 42)
3. Samples `train_samples_per_class` per class for TRAIN, `eval_samples_per_class` for EVAL
4. Saves to local JSONL files:
   ```
   projects/<slug>/data/
   ├── train.jsonl    # {"text": "...", "label": "class_name"}
   └── eval.jsonl     # {"text": "...", "label": "class_name"}
   ```
5. The prep script is run **once** before any training begins (during baseline setup)

The `evaluate.py` script must **only read from the local `data/train.jsonl` and `data/eval.jsonl` files**. It must never download or access the original dataset. This keeps each eval run fast and ensures deterministic splits.

Add `data/` to the project's `.gitignore`.

---

## PR Analytics

```bash
# All rounds from run
gh pr list --search "run-20260304-1430" --state all

# Success rate
MERGED=$(gh pr list --search "run-20260304-1430" --state merged --json number | jq length)
TOTAL=$(gh pr list --search "run-20260304-1430" --state all --json number | jq length)
echo "Success: $MERGED/$TOTAL"
```

---

## Success Criteria

A round succeeds when:
1. Investigation identifies patterns from TRAIN
2. Implementation adds no EVAL leakage
3. Evaluation shows improvement >= min_delta
4. Prompt remains general

---

## Notes

- **Model locked**: Cannot change llm.model during optimization
- **Non-deterministic**: Must re-run EVAL_CMD each time
- **EVAL leakage prevention**: Reviewer checks prompt files
- **Retry learning**: Read rejection evidence before retry
- **Evidence mandate**: All rejections require quantitative proof
