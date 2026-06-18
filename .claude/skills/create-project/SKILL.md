---
name: create-project
description: Use when starting an EPOCH run with no config — the user invokes /epoch without a yaml path or describes an optimization task in conversation. Interviews the user, generates epoch_run.yaml + a project scaffold, validates it runs, then hands off to the optimization loop.
---

# Create Project

Interview the user, generate an EPOCH config + project scaffold, validate it, then hand off
to the round loop. **Owned by the orchestrator** — it runs this before any round when no
config is provided.

## When to Use

- `/epoch` invoked with no config path.
- User describes a task to optimize in conversation ("epoch, classify wine cultivars").

## Discipline

- **No git archaeology.** Do NOT run `git log`/`git show` or read other project folders to
  "follow patterns." Scaffold from the templates here and the user's input only.
- **Confirm before writing.** Show the proposed `epoch_run.yaml` and get approval before
  creating any files. Then confirm again before running anything.
- **3–5 questions max.** Infer everything possible from context.

---

## Step 1: Detect Intent

Identify from the user's message:
- **What** they want to optimize (classification, detection, generation, …)
- **Data source** (sklearn dataset, CSV, API, existing code, …)
- **Task type hint** (rules, prompt, hyperparameters, code)

If unclear, ask:
> What would you like to optimize? For example:
> - "Classify iris species using rules"
> - "Tune my sentiment analysis prompt"
> - "Fix bugs in my sorting algorithm"

## Step 2: Gather Requirements

Ask only what's missing. Every question must allow free-form input (AskUserQuestion's
"Other"). Collect:

| Field | Question | Default |
|-------|----------|---------|
| name | "What should we call this project?" | Derived from task |
| slug | (auto) | snake_case of name |
| task_type | rule_based / prompt_tune / finetune / code_improvement | Inferred |
| data_source | "Where's the data?" | — |
| primary_metric | accuracy / precision / recall / f1 / custom | accuracy |
| max_rounds | "How many rounds?" | 3 |
| git config | Confirm push / PRs / target branch | push=true, PRs=true, target=develop |

**Do NOT ask about:** env (always uv), min_delta (0.01), max_retries (1), internal details.
**ALWAYS confirm git settings** — they affect shared state; never assume silently.

### prompt_tune extras
- `llm.model` (default gpt-4.1-mini), `llm.async` (always true), `llm.concurrency` (12)
- `tune.strategy` (default ["few shots", "chain of thought"]) — applied Rounds 2+, not baseline
- `data.source` + `data.library` (datasets / sklearn / csv)
- `subset`: enabled (true), num_classes (all), train_samples_per_class (10), eval_samples_per_class (6)

### finetune extras
- `ml.device` (cpu / mps / cuda — infer from platform; Apple Silicon → mps)
- `subset`: enabled (true), num_classes (4), train_samples_per_class (10), eval_samples_per_class (4)

## Step 3: Present Config for Confirmation

Before writing files, show the proposed `epoch_run.yaml` and ask
**"Does this config look good? Any changes before I scaffold?"**

ML tasks (prompt_tune, finetune, rule_based) — `evaluation:` with train/eval split:
```yaml
project:
  name: "<name>"
  slug: <slug>
run:
  id: null
  goal: "<goal>"
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

code_improvement — `testing:` with `cmd` + `test_cmd`:
```yaml
project:
  name: "<name>"
  slug: <slug>
run:
  id: null
  goal: "<goal>"
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

Add task-specific sections:
- **prompt_tune**: `llm:`, `tune:`, `subset:`, `data:` — set `deterministic: false`.
- **finetune**: `ml:` (base_model, framework, device), `seed:`, `subset:`.
- **rule_based**: `rules:`.
- **code_improvement**: none — `testing:` covers it.

Only proceed after explicit confirmation. Re-present on requested changes.

## Step 4: Scaffold Project

Only after confirmation, write `projects/<slug>_run.yaml` and:

```
projects/<slug>/
├── pyproject.toml       # task-specific deps
├── prepare_data.py      # prompt_tune, finetune
├── evaluate.py          # reads from data/
├── data/                # generated; add to .gitignore
├── src/prompts/         # prompt_tune: system.txt, task.txt ({text} placeholder)
└── rules/               # rule_based: rules.yaml
```

**pyproject.toml** — rule_based/finetune: `scikit-learn`, `pyyaml`. prompt_tune: `openai`,
`python-dotenv` (+ `datasets` if `data.library: datasets`, `pandas` if csv).

**prepare_data.py** (subset.enabled): load full dataset once → select `num_classes`
(deterministic, seed 42) → sample per-class for TRAIN/EVAL → save local files (prompt_tune:
`data/train.jsonl`/`data/eval.jsonl` with `text`+`label`; finetune: `data/train/<class>/`).
Run once during baseline. Add `data/` to `.gitignore`.

**evaluate.py**: load from local `data/` (never the original dataset), load
rules/model/prompt, predict, print metrics JSON to stdout, save results (incl. failures) to
`<run_id>/<split>_results.json`. One arg: `train` or `eval`. prompt_tune specifics: load
`src/prompts/system.txt`+`task.txt` (prepend `examples.txt` if present), `AsyncOpenAI` with
`asyncio.Semaphore(concurrency)`, `temperature=0`, normalize labels, collect failures.

**rules/rules.yaml** (rule_based): 2–4 conservative starter rules, first-match precedence.

## Step 5: Confirm and Hand Off

Do NOT run eval yet. Summarize what was created (config, files, task_type, metric, rounds)
and ask **"Ready to start optimization?"** On confirm:
1. `uv sync --project projects/<slug>`
2. Run `prepare_data.py` (prompt_tune/finetune)
3. Validate via train_cmd + eval_cmd
4. If valid, hand back to the orchestrator for Phase 1 (Baseline)

---

## Data Source Handling

- **sklearn built-ins**: `sklearn.datasets.load_<name>()` (iris, wine, breast_cancer, digits, …).
- **CSV**: ask path, target column, feature columns; read with pandas.
- **Existing code**: ask path; validate it honors the `train`/`eval` + JSON-output interface.

## Notes

- Keep scaffolding minimal — just enough to run; rounds improve it.
- Don't over-engineer starter rules/prompts. Conservative and simple is correct.
- Description → running `/epoch` in under 2 minutes.
