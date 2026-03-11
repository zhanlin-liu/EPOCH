# Skill: Hyperparameter Fine-Tuning

**Goal**: Optimize ML model hyperparameters to improve evaluation accuracy

**Optimization Target**: Evaluation accuracy on EVAL split

**Version**: Single-agent optimized (all workflows inlined)

---

## Overview

This skill tunes model hyperparameters through iterative adjustment guided by training dynamics analysis. The base model is locked—only hyperparameters listed in the `tune` section can be modified.

**Key Principles:**
- ✅ Only tune parameters defined in the `tune` section of `epoch_run.yaml`
- ✅ Stay within the ranges/options specified for each parameter
- ✅ Investigate training dynamics on TRAIN split only
- ✅ Evaluate improvements on EVAL split only
- ✅ Monitor train-eval gap (overfitting detection)
- ❌ Never change base model architecture
- ❌ Never change parameters not listed in `tune`

---

## Orchestrator: Multi-Round Coordination

### Universal Rules

1. **Config source of truth**: All settings from `epoch_run.yaml`
2. **Canonical commands**: Use TRAIN_CMD/EVAL_CMD from config
3. **Acceptance criteria**: eval_accuracy improves >= min_delta, train_eval_gap < 0.15
4. **Retry logic**: One branch per round; retries on same branch; exceed max → close PR

### Conventions

**Run ID**: `run-YYYYMMDD-HHMM`
**Branch**: `epoch/<project_slug>/<run_id>/round-<N>`

**PR Titles:**
- Round 1: `[Round 1] (Baseline: eval_acc=0.82) Initial hyperparameters`
- Round 2+: `[Round N] (eval_acc: 0.82 → 0.85) Tune learning rate`

### Workflow Steps

**For Each Round (1 to N):**

1. Create/reuse branch (same as prompt tuning)
2. Round 1: Baseline establishment
3. Rounds 2+: Optimization loop (investigation → implementation → evaluation)
4. Handle decision (accept/reject with evidence)

---

## Phase 1: Baseline Establishment (Round 1)

### Seed Planner (Design)

**Task**: Design evaluation approach and read the tunable parameter space from config.

**Deliverables:**
1. Evaluation script interface:
   - Input: data split, hyperparams.json
   - Output: metrics JSON (train_accuracy, train_loss, eval_accuracy, eval_loss)

2. Read the `tune` section from `epoch_run.yaml` to determine:
   - Which parameters are tunable
   - What ranges/options are allowed for each
   - All other training parameters are fixed (read from config, not tunable)

3. Baseline defaults: Pick a conservative starting value for each tunable parameter (first option for lists, low end for ranges)

### Baseline Executor (Implementation)

**Task**: Implement evaluation and establish baseline

**Steps:**
1. Create evaluation script that reads tunable params from `hyperparams.json` and fixed params from `epoch_run.yaml`
2. Create `projects/<slug>/hyperparams.json` containing **only** the parameters listed in `tune`, plus metadata:
   ```json
   {
     "optimizer": "adam",
     "learning_rate": 0.001,
     "metadata": {
       "last_updated_round": 1,
       "updated_by": "baseline_executor",
       "reason": "Initial defaults"
     }
   }
   ```
   Parameters NOT in `tune` (e.g., batch_size, epochs, criterion) are fixed in config and read directly by `evaluate.py`.
3. Implement model training (uses ml.base_model from config)
4. Run TRAIN_CMD, EVAL_CMD
5. Save baseline_metrics.json

---

## Phase 2: Multi-Round Optimization (Rounds 2+)

### Investigation (TRAIN Only)

**Task**: Analyze training dynamics and propose hyperparameter adjustments

**Process:**
1. Train model on TRAIN split
2. Collect training dynamics (loss curves, accuracy progression)
3. Sample N failures (investigation.samples)
4. Analyze for M iterations (investigation.rounds)
5. Diagnose issues:

| Pattern | Diagnosis | Action |
|---------|-----------|--------|
| High train_loss | Underfitting | Increase epochs or learning_rate |
| train_loss plateaus | Local minimum | Reduce learning_rate or change optimizer |
| train_eval_gap > 0.15 | Overfitting | Reduce epochs or add regularization |
| train_loss still decreasing | Not converged | More epochs or adjust LR |

**Retry Detection:**
```bash
git branch -r | grep "round-N"  # Exists → Retry
```

**If Retry:**
1. Read rejection: `gh pr view <PR> --comments`
2. Review what was tried
3. Apply strategy:
   - Small regression + right direction → REFINE (adjust magnitude)
   - Large regression + wrong direction → REVERT (try different hyperparameter)
4. Propose different approach

**Investigation Report:**
```markdown
## Investigation Report - Round N {(RETRY {count})}

**Samples Analyzed**: {investigation.samples} (TRAIN)
**Investigation Rounds**: {investigation.rounds}

{If retry:}
### Previous Attempt
- What tried: learning_rate 0.001 → 0.0005
- Why failed: Still plateaued, needed optimizer change
- What NOT to try: Further LR reduction alone
- New approach: Switch to SGD with momentum

### Current Performance (TRAIN)
- Train accuracy: 0.87
- Train loss: 0.42

### Training Dynamics
- Convergence: Loss plateaued after epoch 7
- Loss curve: Rapid decrease epochs 1-5, minimal change 6-10
- Final epoch: acc=0.87, loss=0.42

### Failure Pattern Analysis
- Pattern 1: Class imbalance - minority class (15 samples)
- Pattern 2: Boundary cases near threshold (20 samples)

### Proposed Hyperparameter Changes
```json
{
  "learning_rate": 0.001,  // Keep (optimizer change addresses plateau)
  "optimizer": "sgd",      // Change from adam (escape local minimum)
  "momentum": 0.9,         // Add for SGD
  "epochs": 15             // Increase (may need more with SGD)
}
```

### Rationale
Loss plateaued with Adam. SGD with momentum can escape local minima better.
Increase epochs to compensate for potentially slower initial convergence.

### Expected Impact
- Train accuracy: 0.87 → 0.90
- Train-eval gap: Maintain < 0.15
```

**Constraints:**
- ✅ TRAIN split only - no EVAL inspection
- ❌ No model architecture changes
- ❌ No base model changes

---

### Implementation

**Task**: Update hyperparameters and commit

**Process:**
1. Read investigation report
2. Update `projects/<slug>/hyperparams.json`:
   - Apply changes
   - Update metadata (round, reason)
3. Validate JSON syntax
4. Run TRAIN_CMD (optional verification)
5. Commit and push

**Allowed:**
- ✅ Parameters listed in `tune` section of `epoch_run.yaml`, within their defined ranges
- ✅ Metadata updates

**Forbidden:**
- ❌ Parameters NOT in `tune` (these are fixed in config)
- ❌ Values outside the ranges defined in `tune`
- ❌ Model architecture
- ❌ Base model
- ❌ Training loop logic

**Commit Format:**
```
Round N{, Retry M}: Adjust hyperparameters for {goal}

- learning_rate: {old} → {new} ({reason})
- optimizer: {old} → {new} ({reason})

Based on investigation: {brief findings}
```

---

### Evaluation (EVAL Only)

**Task**: Evaluate on EVAL and decide with evidence

**Process:**
1. **Mode: Committed results** (deterministic with seeded training)
   ```bash
   # Load proposed from branch
   git show <branch>:projects/<slug>/train_results.json

   # Load baseline from main
   git show main:projects/<slug>/train_results.json
   ```

2. Calculate deltas (all 4 metrics)
3. Check train_eval_gap < 0.15
4. Apply decision logic
5. Generate delta and PR body

**Decision Logic:**

**ACCEPT if:**
- eval_accuracy improvement >= min_delta
- AND train_eval_gap < 0.15
- AND train_loss not diverging

**REJECT if:**
- eval_accuracy decreases
- OR improvement < min_delta
- OR train_eval_gap >= 0.15 (overfitting)
- OR train_loss increases significantly (>0.1)

**CRITICAL: Evidence Required**

**1. Metrics table:**
| Metric | Baseline | Proposed | Delta | Constraint | Status |
|--------|----------|----------|-------|------------|--------|
| eval_accuracy | 0.820 | 0.850 | +0.030 | ≥0.01 | ✅ |
| train_accuracy | 0.870 | 0.900 | +0.030 | - | - |
| train_eval_gap | 0.050 | 0.050 | 0.000 | <0.15 | ✅ |

**2. Training dynamics:**
- How convergence changed
- Loss curve comparison

**3. Root cause (if reject):**
- Why overfitting occurred
- Which hyperparameter caused issue

**4. Retry recommendation:**
- What NOT to try
- Suggested adjustment

**Output Files:**

**delta_round_N.json:**
```json
{
  "round": 2,
  "retry_count": 0,
  "baseline_metrics": {
    "train_accuracy": 0.87, "train_loss": 0.42,
    "eval_accuracy": 0.82, "eval_loss": 0.45
  },
  "proposed_metrics": {
    "train_accuracy": 0.90, "train_loss": 0.35,
    "eval_accuracy": 0.85, "eval_loss": 0.40
  },
  "deltas": {
    "train_accuracy": 0.03, "train_loss": -0.07,
    "eval_accuracy": 0.03, "eval_loss": -0.05,
    "train_eval_gap": 0.05
  },
  "verdict": "ACCEPT",
  "rationale": "eval_accuracy +0.03 (>= 0.01). train_eval_gap 0.05 (< 0.15). All metrics improved."
}
```

**pr_body.md:**
```markdown
## Round N: Hyperparameter Tuning Results {(RETRY {count})}

### Changes
- optimizer: adam → sgd
- momentum: added 0.9
- epochs: 10 → 15

### Metrics

| Metric | Baseline | Proposed | Delta | Constraint | Status |
|--------|----------|----------|-------|------------|--------|
| eval_accuracy | 0.82 | 0.85 | +0.03 | ≥0.01 | ✅ |
| train_accuracy | 0.87 | 0.90 | +0.03 | - | - |
| train_eval_gap | 0.05 | 0.05 | 0.00 | <0.15 | ✅ |

### Verdict: ✅ ACCEPT

**Evidence:**
All metrics improved. No overfitting (gap=0.05 < 0.15 threshold).
SGD with momentum successfully escaped local minimum.
```

**On Accept:**
```bash
gh pr review <PR> --approve --body-file pr_body.md
gh pr merge <PR> --squash --delete-branch
```

**On Reject (example - overfitting):**
```markdown
## Verdict: ❌ REJECT

| Metric | Baseline | Proposed | Delta | Constraint | Status |
|--------|----------|----------|-------|------------|--------|
| eval_accuracy | 0.82 | 0.85 | +0.03 | ≥0.01 | ✅ |
| train_accuracy | 0.87 | 0.95 | +0.08 | - | - |
| train_eval_gap | 0.05 | 0.10 → **0.18** | +0.13 | <0.15 | ❌ |

**Evidence:**
OVERFITTING DETECTED. Gap exceeds threshold (0.18 > 0.15).
Train improved significantly (+0.08) while eval improved minimally (+0.03).

**Root Cause:**
epochs: 15 is too many for this dataset size. Model memorizing TRAIN patterns.

**Recommendation:**
Revert epochs to 10. Try reducing learning_rate instead of increasing epochs.
```

---

## Success Criteria

A round succeeds when:
1. Investigation identifies training dynamics issues
2. Implementation updates hyperparameters correctly
3. Evaluation shows improvement >= min_delta
4. No overfitting (gap < 0.15)

---

## Tune Section (Search Space)

The `tune` section in `epoch_run.yaml` defines **exactly** which parameters the investigator can modify and their allowed ranges. Parameters not listed here are fixed and read directly from the config by `evaluate.py`.

### Config Format

```yaml
tune:
  optimizer: [adam, adamw, sgd]         # List → pick one of these options
  learning_rate: [0.0001, 0.01]         # Two-element numeric list → continuous range [min, max]
  weight_decay: [0.0, 0.1]             # Range for float
  dropout: [0.0, 0.5]                  # Range for float
  batch_size: [8, 16, 32, 64]          # List → pick one of these values
  epochs: [5, 10, 20]                  # List → pick one of these values
```

### Interpretation Rules

| Format | Type | Meaning |
|--------|------|---------|
| `[a, b]` (2 numeric values) | Range | Any value between a and b (inclusive) |
| `[a, b, c, ...]` (3+ values or strings) | Options | Must pick one of the listed values |

### Enforcement

1. **`hyperparams.json` must only contain parameters from `tune`** (plus metadata)
2. **Investigator proposals must stay within ranges** — proposing a value outside the range is forbidden
3. **`evaluate.py` reads tunable params from `hyperparams.json`** and fixed params (batch_size, criterion, etc.) from `epoch_run.yaml` directly
4. **Baseline executor picks conservative defaults**: first option for lists, low-middle of range for numeric ranges

### Example

Config:
```yaml
tune:
  optimizer: [adam, adamw, sgd]
  learning_rate: [0.0001, 0.01]
```

Resulting `hyperparams.json`:
```json
{
  "optimizer": "adam",
  "learning_rate": 0.001,
  "metadata": {
    "last_updated_round": 1,
    "updated_by": "baseline_executor",
    "reason": "Initial defaults (conservative)"
  }
}
```

Fixed params like `batch_size`, `epochs`, `criterion` are NOT in hyperparams.json — they live in `epoch_run.yaml` under `ml` or other sections and are read directly by `evaluate.py`.

---

## Subset Mode

By default, finetune projects use a **subset** of the dataset for fast iteration. The subset config is defined in `epoch_run.yaml`:

```yaml
subset:
  enabled: true
  num_classes: 4
  train_samples_per_class: 10
  eval_samples_per_class: 4
```

When `subset.enabled` is true, create a **separate data prep script** (`projects/<slug>/prepare_data.py`) that:
1. Downloads the full dataset once
2. Selects `num_classes` classes (deterministic selection using SEED)
3. Samples `train_samples_per_class` per class for TRAIN, `eval_samples_per_class` for EVAL
4. Copies the subset images to a local directory structure:
   ```
   projects/<slug>/data/
   ├── train/
   │   ├── class_0/
   │   │   ├── img_001.jpg
   │   │   └── ...
   │   └── class_N/
   └── eval/
       ├── class_0/
       └── class_N/
   ```
5. The prep script is run **once** before any training begins (during baseline setup)

The `evaluate.py` script must **only read from the local `data/train/` and `data/eval/` directories** using `ImageFolder`. It must never download or access the original dataset. This keeps each training/eval run fast (seconds, not minutes).

Set `subset.enabled: false` for a full-dataset run once hyperparameters are tuned.

---

## Reproducibility

All finetune projects must use a **global seed** to ensure reproducible results. The seed is defined in `epoch_run.yaml`:

```yaml
seed: 42
```

The evaluate.py script must apply this seed everywhere:
- `torch.manual_seed(seed)`
- `torch.cuda.manual_seed_all(seed)`
- `np.random.seed(seed)`
- `random.seed(seed)`
- `torch.backends.cudnn.deterministic = True`
- `torch.backends.cudnn.benchmark = False`
- DataLoader `generator=torch.Generator().manual_seed(seed)`
- TRAIN/EVAL split uses the same seed

The seed is read from the config, not hardcoded in evaluate.py.

---

## Device Autodetection

The evaluate.py script must always autodetect the best available device for speed:

```python
if torch.cuda.is_available():
    device = torch.device("cuda")
elif torch.backends.mps.is_available():
    device = torch.device("mps")
else:
    device = torch.device("cpu")
```

Never hardcode a device. This ensures optimal performance on CUDA GPUs, Apple Silicon (MPS), and CPU fallback.

---

## Notes

- **Base model locked**: Cannot change ml.base_model
- **Deterministic**: Global seed ensures reproducible training and evaluation
- **Subset by default**: Use small subset for fast iteration; full dataset for final validation
- **Overfitting detection**: Gap >= 0.15 triggers rejection
- **Retry learning**: Read rejection evidence before retry
- **Evidence mandate**: All rejections require quantitative proof
