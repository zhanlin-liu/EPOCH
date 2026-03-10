# Reference: Create Project

**Goal**: Interview user, generate epoch config + project scaffold, validate, then hand off to main workflow.

**Trigger**: User invokes `/epoch` without a config path, or describes a task in conversation.

---

## Step 1: Detect Intent

Parse the user's message to identify:

- **What** they want to optimize (classification, detection, generation, etc.)
- **Data source** (sklearn dataset, CSV, API, existing code, etc.)
- **Task type hint** (rules, prompt, hyperparameters, code)

If unclear, ask:

> What would you like to optimize? For example:
> - "Classify iris species using rules"
> - "Tune my sentiment analysis prompt"
> - "Fix bugs in my sorting algorithm"

---

## Step 2: Gather Requirements

Ask only what's missing. Skip questions the user already answered. Collect:

| Field | Question | Default |
|-------|----------|---------|
| **name** | "What should we call this project?" | Derived from task description |
| **slug** | (auto-derived from name) | snake_case of name |
| **task_type** | "Which approach?" (rule_based / prompt_tune / finetune / code_improvement) | Inferred from description |
| **data_source** | "Where's the data?" (sklearn built-in / CSV path / existing code) | - |
| **primary_metric** | "What metric to optimize?" (accuracy / precision / recall / f1 / custom) | accuracy |
| **max_rounds** | "How many optimization rounds?" | 3 |
| **git config** | Confirm: push to remote, create PRs, target branch | push=true, PRs=true, target=develop |

**Do NOT ask about:**
- Env settings (always uv)
- min_delta (default 0.01)
- max_retries (default 1)
- Internal details the user doesn't need to decide

**ALWAYS confirm git settings** — present the defaults and ask the user to approve or change them. Git operations (pushing, creating PRs, target branch) affect shared state and should never be silently assumed.

**Goal: 3-5 questions max.** Infer everything possible from context.

**Always allow free-form input.** When using AskUserQuestion, every question must allow the user to type a custom answer (the tool's built-in "Other" option). Never present only fixed choices — the user may have preferences, metrics, or approaches not listed.

### Prompt Tune-Specific Questions

When `task_type` is `prompt_tune`, also ask about the following during the interview:

#### LLM Configuration

| Field | Question | Default |
|-------|----------|---------|
| **llm.model** | "Which LLM model to use?" | gpt-4.1-mini |
| **llm.async** | (don't ask — always true) | true |
| **llm.concurrency** | "Max concurrent API requests?" | 12 |

#### Tune Strategy

| Field | Question | Default |
|-------|----------|---------|
| **tune.strategy** | "Which optimization strategies to try?" | ["few shots", "chain of thought"] |

Options: "few shots", "chain of thought", "system prompt refinement", or custom.
Present defaults and let the user confirm or customize. Strategies are applied in Rounds 2+ only — the baseline uses a plain prompt.

#### Data Configuration

| Field | Question | Default |
|-------|----------|---------|
| **data.source** | "What dataset?" | Inferred from task description |
| **data.library** | "How to load it?" (datasets / sklearn / csv) | Inferred from source |

For HuggingFace datasets, use `data.library: "datasets"`. For sklearn built-ins, use `"sklearn"`. For CSV files, use `"csv"` and ask for the file path.

#### Subset Configuration

Subset mode controls sample sizes per class, keeping each round fast while ensuring balanced splits.

| Field | Question | Default |
|-------|----------|---------|
| **subset.enabled** | "Use subset mode for fast iteration?" | true |
| **subset.num_classes** | "How many classes to include?" | All classes in dataset |
| **subset.train_samples_per_class** | "Training samples per class?" | 10 |
| **subset.eval_samples_per_class** | "Eval samples per class?" | 6 |

Present sensible defaults based on the dataset. If the user accepts defaults, confirm the subset block as a whole rather than asking each field individually.

---

### Finetune-Specific Questions

When `task_type` is `finetune`, also ask about the following during the interview:

#### Device

| Field | Question | Default |
|-------|----------|---------|
| **ml.device** | "What device to train on?" | Inferred from platform |

Options:
- **cpu** — CPU only, no GPU required
- **mps** — Apple Silicon GPU (MacBook Pro M-series)
- **cuda** — NVIDIA GPU

Infer the default from the user's platform when possible (e.g., macOS with Apple Silicon → `mps`). The evaluate.py script should read `ml.device` from the config and use it for model/tensor placement.

#### Subset Configuration

Subset mode keeps each round fast (seconds, not minutes) by using a small slice of the dataset.

| Field | Question | Default |
|-------|----------|---------|
| **subset.enabled** | "Use subset mode for fast iteration?" | true |
| **subset.num_classes** | "How many classes to include in the subset?" | 4 |
| **subset.train_samples_per_class** | "Training samples per class?" | 10 |
| **subset.eval_samples_per_class** | "Eval samples per class?" | 4 |

Present sensible defaults based on the dataset size. If the user accepts defaults, don't ask each field individually — just confirm the subset block as a whole. Only drill into individual fields if the user wants to customize.

---

## Step 3: Present Config for Confirmation

**Before writing any files**, show the user the proposed `epoch_run.yaml` and ask for confirmation. The user must approve the config before any files are created.

Present the config in a code block. The structure differs by task type:

**ML tasks** (prompt_tune, finetune, rule_based) use `evaluation:` with train/eval split:

```yaml
project:
  name: "<name>"
  slug: <slug>

run:
  id: null
  goal: "<user's goal description>"
  task_type: <task_type>
  max_rounds: <max_rounds>
  max_retries_per_round: 1

env:
  manager: uv
  path: "projects/<slug>"

evaluation:
  primary_metric: <primary_metric>
  min_delta: 0.01
  deterministic: true
  train_cmd: "python projects/<slug>/evaluate.py train"
  eval_cmd: "python projects/<slug>/evaluate.py eval"

git:
  push_to_remote: true
  create_prs: true
  target_branch: develop
```

**code_improvement** uses `testing:` with `cmd` (benchmark/evaluate) + `test_cmd` (pytest):

```yaml
project:
  name: "<name>"
  slug: <slug>

run:
  id: null
  goal: "<user's goal description>"
  task_type: code_improvement
  max_rounds: <max_rounds>
  max_retries_per_round: 1

env:
  manager: uv
  path: "projects/<slug>"

testing:
  primary_metric: <primary_metric>
  min_delta: 0.05
  deterministic: true
  cmd: "python projects/<slug>/evaluate.py"
  test_cmd: "pytest projects/<slug>/tests/"

git:
  push_to_remote: true
  create_prs: true
  target_branch: develop
```

Add any task-specific sections as needed by the task type:

- **prompt_tune**: Add `llm:` (model, async, concurrency), `tune:` (strategy), `subset:` (enabled, num_classes, train_samples_per_class, eval_samples_per_class), and `data:` (source, library) sections. Set `deterministic: false`.
- **finetune**: Add `ml:` (base_model, framework, device), `seed:`, and `subset:` sections
- **rule_based**: Add `rules:` section
- **code_improvement**: No additional sections needed — `testing:` covers it

Ask: **"Does this config look good? Any changes before I scaffold the project?"**

If the user requests changes, update the config and re-present. Only proceed to Step 4 after explicit confirmation.

---

## Step 4: Scaffold Project

**Only after the user confirms the config**, write the config file and create the project directory:

1. Write `projects/<slug>_run.yaml`
2. Create project files:

```
projects/<slug>/
├── pyproject.toml       # dependencies (task-specific)
├── prepare_data.py      # data prep script (prompt_tune, finetune)
├── evaluate.py          # evaluation script (reads from data/)
├── data/                # generated by prepare_data.py
│   ├── train.jsonl      # TRAIN split (prompt_tune)
│   └── eval.jsonl       # EVAL split (prompt_tune)
├── src/prompts/         # (if prompt_tune)
│   ├── system.txt       # system instructions
│   └── task.txt         # task template with {text} placeholder
└── rules/               # (if rule_based)
    └── rules.yaml       # starter rules
```

### pyproject.toml Templates

**rule_based / finetune:**
```toml
[project]
name = "<slug>-classifier"
version = "0.1.0"
requires-python = ">=3.10"
dependencies = [
    "scikit-learn>=1.3",
    "pyyaml>=6.0",
]
```

**prompt_tune:**
```toml
[project]
name = "<slug>"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "openai>=1.0",
    "python-dotenv>=1.0",
]
```

Add `"datasets>=2.0"` if `data.library` is `"datasets"`, or `"pandas>=2.0"` if loading CSV.

### prepare_data.py Template (prompt_tune, finetune)

When `subset.enabled` is true, create a data prep script that:
1. Downloads/loads the full dataset once
2. Selects `num_classes` classes (deterministic selection using seed 42)
3. Samples `train_samples_per_class` per class for TRAIN, `eval_samples_per_class` for EVAL
4. Saves to local files:
   - **prompt_tune**: `data/train.jsonl` and `data/eval.jsonl` (one JSON object per line with `text` and `label` fields)
   - **finetune**: `data/train/<class>/` and `data/eval/<class>/` directory structure
5. Prints a summary of the split (num classes, samples per split, class names)

The prep script is run **once** before any training begins (during baseline setup). Add `data/` to `.gitignore`.

### evaluate.py Template

The evaluation script must:
1. Load data from local `data/` directory (created by `prepare_data.py`), NOT from the original dataset
2. Load rules/model/prompt from the project directory
3. Run classification/prediction
4. Print metrics as JSON to stdout
5. Save detailed results (including failures) to `<run_id>/<split>_results.json`

The script takes one argument (`train` or `eval`). Do NOT reference other project folders for patterns — use only the templates in this file.

**prompt_tune evaluate.py specifics:**
- Load prompts from `src/prompts/system.txt` and `src/prompts/task.txt`
- If `src/prompts/examples.txt` exists, prepend it to the task prompt (for few-shot rounds)
- Use `AsyncOpenAI` with `asyncio.Semaphore(concurrency)` for parallel inference
- Set `temperature=0` for reproducibility
- Parse LLM response and normalize to expected label format
- Collect failures with index, input text, expected label, and predicted label

### rules/rules.yaml Template (rule_based only)

Generate 2-4 conservative starter rules based on the dataset. If using a sklearn dataset, briefly inspect feature distributions to pick reasonable initial thresholds. Use first-match precedence.

---

## Step 5: Confirm and Hand Off

**Do NOT run the evaluation commands yet.** Present the user with a summary of what was created:

```
Project scaffolded:
- Config: projects/<slug>_run.yaml
- Files: projects/<slug>/evaluate.py, pyproject.toml, ...
- Task type: <task_type>
- Metric: <primary_metric>
- Rounds: <max_rounds>

Ready to start optimization? (This will install dependencies, validate the scaffold, and begin Round 1.)
```

If user confirms, proceed to the main EPOCH workflow:
1. Run `uv sync --project projects/<slug>` to install dependencies
2. Run `prepare_data.py` to generate local data splits (if prompt_tune or finetune)
3. Validate by running train_cmd and eval_cmd
4. If validation passes, begin Phase 1 (Baseline)

If user wants changes, modify the config/scaffold first.

---

## Data Source Handling

### sklearn built-in datasets

Use `sklearn.datasets.load_<name>()`. Supported: iris, wine, breast_cancer, digits, diabetes, etc.

### CSV files

Ask for the file path, target column, and feature columns. Generate evaluate.py that reads the CSV with pandas.

### Existing code

Ask for the path to existing evaluation code. Validate it works with the expected interface (`train`/`eval` argument, JSON output).

---

## Notes

- Keep scaffolding minimal — just enough to run. EPOCH rounds will improve it.
- Don't over-engineer the starter rules/prompt. Conservative and simple is correct.
- The user should be able to go from description to running `/epoch` in under 2 minutes.
