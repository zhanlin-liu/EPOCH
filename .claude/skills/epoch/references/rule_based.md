# Skill: Rule-Based Optimization

**Goal**: Optimize rule-based systems to improve evaluation accuracy

**Optimization Target**: Evaluation accuracy (or other metric) on EVAL split

**Version**: Single-agent optimized (all workflows inlined)

---

## Overview

This skill optimizes rule-based systems through iterative rule refinement. Rules are modified based on failure pattern analysis while preventing EVAL-specific over-fitting.

**Key Principles:**
- ✅ Investigate failures on TRAIN split only
- ✅ Evaluate improvements on EVAL split only
- ✅ Maintain rule precedence consistency
- ❌ Never create EVAL-specific rules

---

## Orchestrator: Multi-Round Coordination

### Universal Rules

1. **Config source of truth**: All settings from `epoch_run.yaml`
2. **Canonical commands**: Use TRAIN_CMD/EVAL_CMD from config
3. **Acceptance criteria**: Primary metric improves >= min_delta, no EVAL-specific rules
4. **Retry logic**: One branch per round; retries on same branch; exceed max → close PR

### Conventions

**Run ID**: `run-YYYYMMDD-HHMM`
**Branch**: `epoch/<project_slug>/<run_id>/round-<N>`

**PR Titles:**
- Round 1: `[Round 1] (Baseline: precision=0.75) Initial ruleset`
- Round 2+: `[Round N] (precision: 0.75 → 0.82) Adjust thresholds`

### Workflow (same structure as other tasks)

---

## Phase 1: Baseline Establishment (Round 1)

### Seed Planner (Design)

**Task**: Design rule structure and evaluation

**Deliverables:**
1. Evaluation script interface
2. Rule structure design:
   - Format: if-then, weighted scoring, decision tree
   - Precedence strategy: first-match, weighted-voting, priority-based
   - Rule actions
   - Feature space
3. Baseline ruleset: Initial rules with conservative thresholds

### Baseline Executor (Implementation)

**Task**: Implement evaluation and establish baseline

**Steps:**
1. Create evaluation script
2. Create rule files in `projects/<slug>/rules/`:
   - `rules.yaml` or `rules.py` - Rule definitions
3. Implement rule engine
4. Run TRAIN_CMD, EVAL_CMD
5. Save baseline_metrics.json

---

## Phase 2: Multi-Round Optimization (Rounds 2+)

### Investigation (TRAIN Only)

**Task**: Analyze TRAIN failures and propose rule improvements

**Process:**
1. Run rule evaluation on TRAIN split
2. Sample N failures (investigation.samples)
3. Analyze patterns (investigation.rounds iterations)
4. Identify failure types:
   - **False positives**: Rules triggering incorrectly (precision issue)
   - **False negatives**: Rules missing cases (recall issue)
   - **Threshold issues**: Boundaries not optimal
   - **Coverage gaps**: No rule handles pattern
   - **Precedence conflicts**: Rule order causing errors
   - **Feature correlation**: Rules ignore interactions
5. Propose rule modifications

**Rule Modification Strategies:**
- Add rules: Cover new patterns
- Modify thresholds: Adjust boundaries
- Adjust weights: Change importance
- Remove rules: Eliminate harmful rules
- Reorder rules: Fix precedence conflicts

**Retry Detection and Protocol** (same as other tasks)

**Investigation Report:**
```markdown
## Investigation Report - Round N {(RETRY {count})}

**Samples Analyzed**: {investigation.samples} (TRAIN)
**Investigation Rounds**: {investigation.rounds}

{If retry: previous attempt analysis}

### Current Performance (TRAIN)
- Train accuracy: {value}
- Train precision: {value}
- Train recall: {value}

### Failure Pattern Analysis

**Pattern 1: False Positives - Large Transactions** (22 samples, 44%)
- Description: Legitimate large transactions flagged as fraud
- Examples:
  - amount=1500, frequency=1, location=home → Expected: legitimate → Got: fraud
  - amount=2000, merchant=trusted, history=5yrs → Expected: legitimate → Got: fraud
- Root cause: Rule "amount > 1000 → fraud" too aggressive

**Pattern 2: False Negatives - Small Frequent** (15 samples, 30%)
- Description: Small fraudulent transactions slip through
- Examples:
  - amount=50, frequency=20/day, new_location=yes → Expected: fraud → Got: legitimate
- Root cause: No rule for high-frequency small amounts

### Current Rules (relevant)
```yaml
rules:
  - name: "high_amount_flag"
    condition: "amount > 1000"
    weight: 0.8
    action: "flag_fraud"
```

### Proposed Rule Changes

**Change 1: Raise Amount Threshold**
- File: projects/<slug>/rules/rules.yaml
- Rule: high_amount_flag
- Current: amount > 1000
- Proposed: amount > 2500
- Rationale: Addresses Pattern 1 (44% of failures)

**Change 2: Add High-Frequency Rule**
- File: projects/<slug>/rules/rules.yaml
- New rule:
  ```yaml
  - name: "high_frequency_small"
    condition: "amount < 100 AND frequency > 10/day"
    weight: 0.7
    action: "flag_fraud"
  ```
- Rationale: Addresses Pattern 2 (30% of failures)

### Expected Impact
- Precision: 0.75 → 0.85 (fewer false positives)
- Recall: 0.70 → 0.75 (catch high-frequency pattern)
```

**Constraints:**
- ✅ TRAIN split only
- ❌ No EVAL-specific rules

---

### Implementation

**Task**: Modify rule files and commit

**Process:**
1. Read investigation report
2. Update rule files (YAML or Python)
3. Validate rule syntax
4. Run TRAIN_CMD (verification)
5. Commit and push

**Example Modifications:**

**YAML format:**
```yaml
rules:
  - name: "high_amount_flag"
    condition: "amount > 2500"  # Raised threshold
    weight: 0.8
    action: "flag_fraud"

  - name: "high_frequency_small"  # New rule
    condition: "amount < 100 AND frequency > 10"
    weight: 0.7
    action: "flag_fraud"
```

**Python format:**
```python
def evaluate_rules(sample):
    score = 0

    # Modified threshold
    if sample['amount'] > 2500:  # Was 1000
        score += 0.8

    # New rule
    if sample['amount'] < 100 and sample['frequency'] > 10:
        score += 0.7

    return score > threshold
```

**Allowed:**
- ✅ Rule conditions (thresholds, operators)
- ✅ Rule weights/priorities
- ✅ Add/remove rules
- ✅ Rule actions

**Forbidden:**
- ❌ EVAL-specific rules (conditions matching only EVAL)
- ❌ Evaluation logic
- ❌ Feature extraction (unless in scope)

**Commit Format:**
```
Round N{, Retry M}: {Brief summary}

- Modified rule: high_amount_flag threshold 1000→2500
- Added rule: high_frequency_small for small rapid transactions

Based on investigation: 44% false positives on large legitimate amounts
```

---

### Evaluation (EVAL Only)

**Task**: Evaluate on EVAL and decide with evidence

**Process:**
1. **Mode: Committed results** (deterministic rule evaluation)
   ```bash
   git show <branch>:projects/<slug>/rule_results.json
   git show main:projects/<slug>/rule_results.json
   ```

2. Calculate deltas
3. Check for EVAL-specificity (rule distribution analysis)
4. Apply decision logic
5. Generate delta and PR body

**Decision Logic:**

**ACCEPT if:**
- Primary metric (accuracy/precision/recall/F1) improves >= min_delta
- AND no EVAL-specific rules detected
- AND rule set remains maintainable

**REJECT if:**
- Primary metric decreases
- OR improvement < min_delta
- OR EVAL-specific rules detected
- OR rule complexity excessive

**EVAL-Specificity Detection:**
- Rules matching only EVAL samples
- Thresholds suspiciously tailored to EVAL distribution
- Large TRAIN vs EVAL metric gap

**CRITICAL: Evidence Required**

**1. Metrics table:**
| Metric | Baseline | Proposed | Delta | Threshold | Status |
|--------|----------|----------|-------|-----------|--------|
| precision | 0.750 | 0.850 | +0.100 | ≥0.01 | ✅ |
| recall | 0.700 | 0.750 | +0.050 | - | - |
| F1 | 0.724 | 0.797 | +0.073 | - | - |

**2. Rule analysis:**
- Which rules triggered more/less
- Distribution on TRAIN vs EVAL

**3. Root cause (if reject):**
- Why EVAL-specific
- Which rule is problematic

**4. Retry recommendation:**
- More general threshold
- Different rule approach

**Output Files (same format as other tasks)**


---

## Success Criteria

A round succeeds when:
1. Investigation identifies failure patterns from TRAIN
2. Implementation modifies rules without EVAL-specificity
3. Evaluation shows improvement >= min_delta
4. Rule set remains maintainable

---

## Notes

- **Rule complexity**: Balance coverage with maintainability
- **Precedence matters**: Rule order significantly impacts results
- **Deterministic**: Use committed results (rules are deterministic)
- **Feature engineering**: May need new features if patterns can't be expressed
- **Retry learning**: Read rejection evidence before retry
