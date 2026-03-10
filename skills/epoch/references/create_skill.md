# Skill: Create New Skill

**Goal**: Generate new skill files from free-form goal description

**Output**: Self-contained skill.md with all workflows inlined

---

## Purpose

This meta-workflow enables users to create new optimization skills by describing what they want to optimize. The skill uses AI-driven context detection to understand intent, ask relevant questions, and generate a complete self-contained skill file.

**v2-consolidated architecture benefits:**
- Generated skills are self-contained (all workflows inlined)
- Works in single-agent environments (no sub-agent spawning needed)
- Lower total context (~400-450 lines vs 1,400 lines for v2 with all shared workflows)
- Simpler to understand and use

---

## Input Format

**Single required field:**
```yaml
goal: "What you want to optimize"
```

**Examples:**
- "Optimize my sentiment classification prompt"
- "Tune hyperparameters for image classifier"
- "Fix bugs in my sorting algorithm"
- "Improve rule-based fraud detection"

---

## Process

### Step 1: Baseline Status Detection

Ask user if they have existing evaluation code:

```
Q0: "Do you have existing evaluation code for this task?"

Options:
1. "No, create everything from scratch (Recommended)"
   - Skill will include full Phase 1 (Seed Planner + Baseline Executor)

2. "Yes, I have evaluation script and baseline code"
   - Skill will include validation-only Phase 1
   - User must provide baseline_path and optionally baseline_metrics_path
```

**Output:**
- `baseline.create_from_scratch`: true or false
- `baseline.baseline_path`: null or path
- `baseline.baseline_metrics_path`: null or path

---

### Step 2: Context Detection

**Parse goal text to detect optimization domain:**

| Keywords | Detected Context | Reference Skill |
|----------|------------------|----------------|
| "prompt", "LLM", "GPT", "Claude", "instructions" | Prompt tuning | v2-consolidated/prompt_tune.md |
| "hyperparameter", "learning rate", "batch size", "optimizer" | Fine-tuning | v2-consolidated/finetune.md |
| "rules", "conditions", "thresholds", "if-then" | Rule-based | v2-consolidated/rule_based.md |
| "algorithm", "code", "bug", "test", "debug", "leetcode" | Code improvement | v2-consolidated/code_improvement.md |

**If confidence < 70%:** Ask user to clarify

**Output:** Detected context + reference skill to use as template

---

### Step 3: Context-Specific Q&A

**Ask task-specific questions:**

#### For Prompt Tuning:
1. Q: "What LLM model?" (gpt-4, claude-3-opus, claude-sonnet-4, other)
2. Q: "Describe your dataset" (free text)
3. Q: "What metric to optimize?" (accuracy, f1, precision, recall, custom)

#### For Fine-Tuning:
1. Q: "What's your base model?" (free text)
2. Q: "Which hyperparameters to tune?" (multi-select: lr, batch_size, optimizer, epochs, etc.)
3. Q: "Describe your dataset" (free text)
4. Q: "What metric to optimize?" (eval_accuracy, eval_loss, f1, other)

#### For Rule-Based:
1. Q: "Describe your rule structure" (free text)
2. Q: "How many initial rules?" (1-5, 6-10, 11-20, 20+, from scratch)
3. Q: "What metric to optimize?" (accuracy, precision, recall, f1, other)

#### For Code Improvement:
1. Q: "Describe the problem" (free text)
2. Q: "Do you have a test suite?" (pytest, unittest, LeetCode-style, no)
3. Q: "Optimization goal?" (correctness only, performance only, both)

**Output:** Complete requirement specification

---

### Step 4: Generate v2-Consolidated Skill File

**Generate self-contained skill with all workflows inlined:**

The generated skill should follow this structure (adapt from reference skill):

```markdown
# Skill: {Derived from user's goal} (v2-Consolidated)

**Goal**: {User's goal text}
**Optimization Target**: {Metric} on EVAL split
**Version**: Single-agent optimized (all workflows inlined)

---

## Overview

{Brief description with key principles}

**Key Principles:**
- ✅ {Principle 1}
- ✅ {Principle 2}
- ❌ {Anti-pattern 1}
- ❌ {Anti-pattern 2}

---

## Orchestrator: Multi-Round Coordination

### Universal Rules

1. **Config source of truth**: All settings from epoch_run.yaml
2. **Canonical commands**: Use TRAIN_CMD/EVAL_CMD from config
3. **Acceptance criteria**: {metric} improves >= min_delta
4. **Retry logic**: One branch per round; retries on same branch; exceed max → close PR

### Conventions

**Run ID**: `run-YYYYMMDD-HHMM`
**Branch**: `epoch/<project_slug>/<run_id>/round-<N>`

**PR Titles:**
- Round 1: `[Round 1] (Baseline: {metric}={value}) Initial {artifact}`
- Round 2+: `[Round N] ({metric}: {old} → {new}) {Brief summary}`

### Workflow (same structure, task-specific decisions)

---

## Phase 1: Baseline Establishment (Round 1)

{If create_from_scratch=true:}

### Seed Planner (Design)

**Task**: Design {task-specific deliverable}

**Deliverables:**
1. {Deliverable 1}
2. {Deliverable 2}
3. Baseline: {Initial approach}

### Baseline Executor (Implementation)

**Task**: Implement evaluation and establish baseline

**Steps:**
1. Create evaluation script
2. Create {task-specific artifacts}
3. Implement {task-specific logic}
4. Run TRAIN_CMD, EVAL_CMD
5. Save baseline_metrics.json

{If create_from_scratch=false:}

### Baseline Validation

**NOTE**: User has provided existing code at {baseline_path}

**Task**: Validate existing baseline

**Steps:**
1. Verify evaluation script works
2. Run TRAIN_CMD, EVAL_CMD
3. Load or generate baseline_metrics.json

---

## Phase 2: Multi-Round Optimization (Rounds 2+)

### Investigation (TRAIN Only)

**Task**: Analyze {artifact} and propose improvements

**Process:**
1. Run {task-specific analysis} on TRAIN split
2. Sample N failures (investigation.samples)
3. Analyze patterns (investigation.rounds iterations)
4. Identify failure types:
   - {Failure type 1}
   - {Failure type 2}
   - {Failure type 3}
5. Propose {artifact} modifications

**Retry Detection:**
```bash
git branch -r | grep "round-N"  # Exists → Retry
```

**If Retry:**
1. Read rejection: `gh pr view <PR> --comments`
2. Review what was tried
3. Apply strategy:
   - Small regression + right direction → REFINE (adjust magnitude)
   - Large regression + wrong direction → REVERT (try different approach)
4. Propose different approach

**Investigation Report:**
```markdown
## Investigation Report - Round N {(RETRY {count})}

**Samples Analyzed**: {investigation.samples} (TRAIN)
**Investigation Rounds**: {investigation.rounds}

{If retry:}
### Previous Attempt
- What tried: {previous change}
- Why failed: {root cause}
- What NOT to try: {avoid this}
- New approach: {different strategy}

### Current Performance (TRAIN)
- {metric 1}: {value}
- {metric 2}: {value}

### Failure Pattern Analysis

**Pattern 1: {Pattern name}** ({count} samples, {percentage}%)
- Description: {what's failing}
- Examples:
  - {example 1}
  - {example 2}
- Root cause: {why it fails}

**Pattern 2: {Pattern name}** ({count} samples, {percentage}%)
- Description: {what's failing}
- Root cause: {why it fails}

### Proposed Changes

**Change 1: {Change description}**
- File: {file path}
- Current: {current state}
- Proposed: {new state}
- Rationale: Addresses Pattern 1 ({percentage}% of failures)

**Change 2: {Change description}**
- Rationale: Addresses Pattern 2

### Expected Impact
- {metric}: {old} → {predicted new} ({delta})
```

**Constraints:**
- ✅ TRAIN split only
- ❌ {Task-specific constraint}

---

### Implementation

**Task**: Modify {artifact} and commit

**Process:**
1. Read investigation report
2. Apply changes to {files}
3. Validate {validation check}
4. Run TRAIN_CMD (verification)
5. Commit and push

**Allowed:**
- ✅ {Allowed change 1}
- ✅ {Allowed change 2}

**Forbidden:**
- ❌ {Forbidden change 1}
- ❌ {Forbidden change 2}

**Commit Format:**
```
Round N{, Retry M}: {Brief summary}

- {Change 1 description}
- {Change 2 description}

Based on investigation: {brief findings}
```

---

### Evaluation (EVAL Only)

**Task**: Evaluate on EVAL and decide with evidence

**Process:**
1. **Mode: {Committed results or Re-run}**
   ```bash
   {Command to get results}
   ```

2. Calculate deltas
3. {Task-specific checks}
4. Apply decision logic
5. Generate delta and PR body

**Decision Logic:**

**ACCEPT if:**
- {primary metric} improvement >= min_delta
- AND {constraint 1}
- AND {constraint 2}

**REJECT if:**
- {primary metric} decreases
- OR improvement < min_delta
- OR {constraint violation}

**CRITICAL: Evidence Required**

**1. Metrics table:**
| Metric | Baseline | Proposed | Delta | Threshold | Status |
|--------|----------|----------|-------|-----------|--------|
| {metric} | {old} | {new} | {delta} | {threshold} | {✅/❌} |

**2. {Task-specific evidence}:**
- {Evidence type 1}
- {Evidence type 2}

**3. Root cause (if reject):**
- Why {issue}
- Which {artifact} caused it

**4. Retry recommendation:**
- What NOT to try
- Suggested {approach}

**Output Files:**

**delta_round_N.json:**
```json
{
  "round": N,
  "retry_count": 0,
  "baseline_metrics": {
    "{metric1}": {value},
    "{metric2}": {value}
  },
  "proposed_metrics": {
    "{metric1}": {value},
    "{metric2}": {value}
  },
  "deltas": {
    "{metric1}": {delta},
    "{metric2}": {delta}
  },
  "verdict": "ACCEPT/REJECT",
  "rationale": "{explanation}"
}
```

**pr_body.md:**
```markdown
## Round N: {Summary} {(RETRY {count})}

### Changes
- {Change 1}
- {Change 2}

### Metrics

| Metric | Baseline | Proposed | Delta | Constraint | Status |
|--------|----------|----------|-------|------------|--------|
| {metric} | {old} | {new} | {delta} | {threshold} | {✅/❌} |

### Verdict: {✅ ACCEPT / ❌ REJECT}

**Evidence:**
{Detailed evidence}
```


---

## Success Criteria

A round succeeds when:
1. Investigation identifies {patterns} from TRAIN
2. Implementation modifies {artifact} correctly
3. Evaluation shows improvement >= min_delta
4. {Task-specific criterion}

---

## Notes

- **{Note 1}**: {Description}
- **{Note 2}**: {Description}
- **Retry learning**: Read rejection evidence before retry
```

**Key differences from v2:**
- All workflow content is inlined (no external references)
- Orchestrator, Investigator, Executor, Reviewer sections are all in one file
- No need to read separate shared workflow files
- Optimized for single-agent execution

---

### Step 5: Generate Configuration File

**Create epoch_run.yaml:**

```yaml
project:
  name: "{Derived from goal}"
  slug: "{snake_case_slug}"
  description: "{Goal description}"

run:
  task_type: "{detected_context}"
  max_rounds: 10
  max_retries_per_round: 2

baseline:
  create_from_scratch: {true|false}
  baseline_path: {null|path}
  baseline_metrics_path: {null|path}

# Task-specific configuration from Q&A
llm:  # For prompt_tune
  model: {from Q&A}

ml:  # For finetune
  base_model: {from Q&A}
  tunable_hyperparameters: {from Q&A}

rules:  # For rule_based
  format: {from Q&A}
  precedence_strategy: {from Q&A}
  max_rules: {from Q&A}

evaluation:
  primary_metric: {from Q&A}
  min_delta: 0.01
  deterministic: {true for finetune/rule/code, false for prompt}
  train_cmd: "{generated command}"
  eval_cmd: "{generated command}"
  constraints:
    max_train_eval_gap: 0.15  # If ML task

investigation:
  samples: 50
  rounds: 3

git:
  push_to_remote: true
  create_prs: true
  main_branch: "main"
```

---

### Step 6: Save and Commit

**Save files:**
- `skills/v2-consolidated/{slug}.md` - Generated skill (~400-450 lines)
- `projects/{slug}/epoch_run.yaml` - Configuration

**Commit:**
```bash
git add skills/v2-consolidated/{slug}.md projects/{slug}/epoch_run.yaml
git commit -m "Add {slug} skill (v2-consolidated)

Goal: {user goal}
Context: {detected context}
Scenario: {create_from_scratch status}
Architecture: Single-agent optimized
"
```

---

## v2-Consolidated Advantages

### Compared to v2 (Multi-Agent)

**v2 (Multi-Agent):**
- Per-agent context: 460-560 lines (lightweight skill + 1 workflow)
- Total context if all roles needed: 1,400 lines (skill + 4 workflows)
- Works: IF orchestrator can spawn sub-agents
- Maintenance: Easy (update shared workflow, all skills inherit)

**v2-Consolidated (Single-Agent):**
- Total context: 400-450 lines (everything in one file)
- Works: Always (no sub-agent spawning needed)
- Maintenance: Medium (update each skill separately)
- Simpler: Everything in one place

### Compared to v1

**v1:**
- Generated skill: ~500 lines
- Embedded everything (workflows, examples)
- No retry protocol
- No evidence requirements

**v2-Consolidated:**
- Generated skill: ~400-450 lines
- Embedded workflows, separate examples
- Full retry protocol
- Mandatory evidence
- All 8 enhancements from template analysis

---

## Example: Sentiment Classification

**Input:**
```yaml
goal: "Optimize my sentiment classification prompt"
```

**AI Flow:**

1. **Baseline Detection:**
   - Q: "Have existing code?" → A: "No, create from scratch"
   - Set: create_from_scratch = true

2. **Context Detection:**
   - Keywords: "prompt", "classification"
   - Context: Prompt tuning (95% confidence)
   - Reference: v2-consolidated/prompt_tune.md

3. **Q&A:**
   - Model: "gpt-4"
   - Dataset: "Movie reviews, 5K train, 2K eval, binary sentiment"
   - Metric: "accuracy"

4. **Generated:** `skills/v2-consolidated/sentiment_prompt_tune.md` (420 lines)

   Content includes (all inlined):
   - Orchestrator coordination logic
   - Investigation workflow (TRAIN-only pattern analysis)
   - Implementation workflow (prompt modification)
   - Evaluation workflow (EVAL-only decision making with evidence)
   - Complete retry protocol
   - Evidence-based rejection requirements
   - Task-specific patterns and constraints

5. **Configuration:** `projects/sentiment_classification/epoch_run.yaml`
   ```yaml
   llm:
     model: "gpt-4"
   evaluation:
     primary_metric: "accuracy"
     train_cmd: "python projects/sentiment_classification/evaluate.py train"
     eval_cmd: "python projects/sentiment_classification/evaluate.py eval"
   ```

**Result:** Ready-to-use v2-consolidated skill in <5 minutes

---

## Validation Rules

**Generated skill must:**
- ✅ Be self-contained (no external workflow references)
- ✅ Be ~400-450 lines (all workflows inlined)
- ✅ Include complete orchestrator section
- ✅ Include complete investigation section (with retry protocol)
- ✅ Include complete implementation section
- ✅ Include complete evaluation section (with evidence requirements)
- ✅ Specify task-specific constraints clearly
- ✅ Include configuration requirements
- ✅ Include success criteria
- ✅ Handle both create_from_scratch scenarios

**Generated epoch_run.yaml must:**
- ✅ Include all v2 fields (max_retries_per_round, deterministic, constraints)
- ✅ Include baseline configuration (create_from_scratch, paths)
- ✅ Include task-specific configuration
- ✅ Match skill requirements exactly

---

## When to Use v2-Consolidated vs v2

**Use v2-consolidated when:**
- ✅ Single-agent environment (no sub-agent spawning)
- ✅ Want simpler, self-contained skills
- ✅ Context efficiency is priority (450 vs 1,400 lines)
- ✅ Quick start is important

**Use v2 when:**
- ✅ Multi-agent environment (orchestrator spawns sub-agents)
- ✅ Maintenance of shared workflows is priority
- ✅ Multiple task types will be created
- ✅ Per-agent context optimization needed

---

## Reference Materials

When generating skills, refer to these specifications:

**Agents** (see [agents/](../agents/)):
- [orchestrator.md](../agents/orchestrator.md) - Multi-round coordination, branching, PR management
- [seed_planner.md](../agents/seed_planner.md) - Baseline design and planning
- [baseline_executor.md](../agents/baseline_executor.md) - Baseline implementation
- [investigator.md](../agents/investigator.md) - Failure analysis and retry protocols
- [executor.md](../agents/executor.md) - Implementation guidelines
- [reviewer.md](../agents/reviewer.md) - Evidence-based evaluation

**Task-Type References** (see [references/](../references/)):
- [prompt_tune.md](../references/prompt_tune.md) - LLM prompt optimization
- [finetune.md](../references/finetune.md) - ML hyperparameter tuning
- [rule_based.md](../references/rule_based.md) - Rule-based system optimization
- [code_improvement.md](../references/code_improvement.md) - Bug fixes and performance

These files provide detailed examples of:
- Evidence-based rejection protocols
- Retry state management and decision matrices
- Investigation report templates
- PR body formats with metrics tables
- Git workflow patterns
- Deterministic evaluation modes

Use these as references when inlining workflows into generated skills.

---

## Notes

- **Self-contained**: Generated skills include all workflows inlined
- **Single-agent optimized**: Lower total context for single-agent execution
- **All enhancements**: Includes all 8 improvements from template analysis
- **Consistent structure**: All generated skills follow same consolidated pattern
- **Reference-driven**: Use docs/workflows/ as authoritative examples when generating
