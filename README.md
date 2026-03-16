# EPOCH

Multi-round optimization framework that runs iterative optimize-evaluate loops: investigate failures, implement a fix, evaluate the result, accept or reject with evidence, repeat. Works with both [Claude Code](https://docs.anthropic.com/en/docs/claude-code) and [OpenAI Codex](https://github.com/openai/codex).

## Installation

### Claude Code

```bash
claude plugin marketplace add zhanlin-liu/EPOCH
claude plugin install epoch@zhanlin-liu-EPOCH
```

Then use `/epoch` in any project.

### OpenAI Codex

```
$skill-installer install https://github.com/zhanlin-liu/EPOCH/tree/main/skills/epoch
```

Restart Codex after installation, then use `/epoch`.

### From Source

```bash
git clone https://github.com/zhanlin-liu/EPOCH.git
cd EPOCH
claude  # or codex
```

## Quick Start

### Option 1: Guided Setup (No Config)

```
/epoch
```

EPOCH will interview you (3–5 questions) and scaffold the project automatically.

### Option 2: Existing Config

```
/epoch projects/my_project_run.yaml
```

EPOCH reads the config, sets up the environment, and starts the optimization loop.

## Supported Task Types

| Task Type | What It Optimizes | Example |
|-----------|-------------------|---------|
| `prompt_tune` | LLM prompt text | Sentiment classification with GPT-4.1-nano |
| `finetune` | ML hyperparameters | MobileNetV2 learning rate and optimizer |
| `rule_based` | Rule conditions and thresholds | Iris species classifier |
| `code_improvement` | Algorithm correctness and performance | Fibonacci calculator speed |

## How It Works

```
Round 1: Baseline
  └─ Scaffold project → Run evaluation → Save baseline metrics → Open PR

Round 2+: Optimization Loop
  └─ Investigate failures (TRAIN only)
     └─ Implement fix
        └─ Evaluate (EVAL only)
           ├─ ACCEPT → Merge PR → Next round
           └─ REJECT → Retry or next round
```

Each round produces:
- A git branch (`epoch/<slug>/<run-id>/round-N`)
- A pull request with metrics tables and evidence
- Structured JSON artifacts (`baseline_metrics.json`, `delta_round_N.json`)

## Plugin Structure

```
.claude-plugin/
└── plugin.json
skills/
└── epoch/
    ├── SKILL.md                    # Entry point — dispatches by task_type
    ├── agents/                     # Role definitions
    │   ├── orchestrator.md
    │   ├── investigator.md
    │   ├── executor.md
    │   ├── baseline_executor.md
    │   ├── seed_planner.md
    │   └── reviewer.md
    └── references/                 # Task-type workflows
        ├── prompt_tune.md
        ├── finetune.md
        ├── rule_based.md
        ├── code_improvement.md
        ├── create_project.md
        └── create_skill.md
```

## Writing a Config

Create `projects/<slug>_run.yaml`. See [`projects/`](projects/) for example configs.

### ML Tasks (prompt_tune, finetune, rule_based)

```yaml
project:
  name: "My Classifier"
  slug: my_classifier

run:
  id: null                    # auto-generated at runtime
  goal: "Optimize classification accuracy"
  task_type: rule_based       # or prompt_tune, finetune
  max_rounds: 5
  max_retries_per_round: 1

env:
  manager: uv
  path: "projects/my_classifier"

evaluation:
  primary_metric: accuracy
  min_delta: 0.01             # minimum improvement to accept a round
  deterministic: true
  train_cmd: "python projects/my_classifier/evaluate.py train"
  eval_cmd: "python projects/my_classifier/evaluate.py eval"

git:
  push_to_remote: true
  create_prs: true
  target_branch: develop
```

### Code Improvement

```yaml
project:
  name: "My Algorithm"
  slug: my_algo

run:
  task_type: code_improvement
  max_rounds: 5
  max_retries_per_round: 1

env:
  manager: uv
  path: "projects/my_algo"

evaluation:
  primary_metric: execution_time
  min_delta: 0.05             # 5% minimum speedup per round
  deterministic: true
  cmd: "python projects/my_algo/main.py"
  test_cmd: "pytest projects/my_algo/tests/"

git:
  push_to_remote: true
  create_prs: true
  target_branch: develop
```

### Hyperparameter Tuning (finetune)

Add `ml` and `tune` sections to control the search space:

```yaml
ml:
  base_model: mobilenetv2
  framework: pytorch
  seed: 42
  max_train_epochs: 3

tune:
  optimizer: [adam, adamw, sgd]       # discrete options
  learning_rate: [0.0001, 0.01]      # continuous range [min, max]
```

### Prompt Tuning (prompt_tune)

Add `llm` and `tune` sections:

```yaml
llm:
  model: "gpt-4.1-nano"
  async: true
  concurrency: 12

tune:
  strategy: ["few shots", "chain of thought"]
```

## Key Concepts

### Train/Eval Separation

For ML tasks, EPOCH enforces strict separation:
- **Investigation**: Analyzes failures on TRAIN split only
- **Evaluation**: Accepts/rejects based on EVAL split only
- This prevents overfitting to the evaluation set

For `code_improvement`: all tests are visible (no split needed).

### Acceptance Criteria

A round is accepted when:
1. Primary metric improves ≥ `min_delta`
2. No constraint violations (e.g., overfitting threshold for finetune)
3. Evidence is provided (metrics table + rationale)

Every rejection requires quantitative evidence — no subjective judgments.

### Retry Protocol

When a round is rejected and retries remain:
- **REFINE**: Small regression → adjust magnitude
- **REVERT**: Large regression → try a different approach entirely

### Git Workflow

- `main` — stable merged results
- `develop` — integration branch
- `epoch/<slug>/<run-id>/round-<N>` — per-round branches

Each round creates a PR with metrics tables. Accepted rounds are squash-merged.

## Examples

### Completed Experiments

| Project | Task Type | Result |
|---------|-----------|--------|
| Fibonacci | `code_improvement` | 6,331x speedup in 4 rounds |
| Sentiment (GPT-4.1-nano) | `prompt_tune` | 0.83 → 1.00 eval accuracy in 3 rounds |
| MNIST (MobileNetV2) | `finetune` | 0.53 → 0.67 eval accuracy in 3 rounds |
| Iris | `rule_based` | 0.98 → 1.00 eval accuracy in 2 rounds |

Demo code is available on the [`examples/demo-projects`](https://github.com/zhanlin-liu/EPOCH/tree/examples/demo-projects) branch.

## Citation

If you use EPOCH in your research, please cite:

```bibtex
@article{liu2026epoch,
  title={EPOCH: An Agentic Protocol for Multi-Round System Optimization},
  author={Liu, Zhanlin and Li, Yitao and Srikanth, Munirathnam},
  journal={arXiv preprint arXiv:2603.09049},
  year={2026}
}
```

## Requirements

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) CLI
- [uv](https://docs.astral.sh/uv/) package manager
- Git with GitHub CLI (`gh`) for PR management
