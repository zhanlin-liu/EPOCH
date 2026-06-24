"""Shared helpers for EPOCH prompt-tuning optimizer scripts (standard contract).

Self-contained per skill so each method skill stays independent. TRAIN-only:
nothing here reads eval.jsonl.
"""
import json
import os
import re

try:
    from dotenv import load_dotenv
except Exception:  # pragma: no cover
    load_dotenv = None


def _repo_root_from(project):
    # project is projects/<slug>; repo root is two levels up.
    return os.path.abspath(os.path.join(project, "..", ".."))


def ensure_env(project):
    """Load OPENAI_API_KEY from repo-root .env if present."""
    if load_dotenv:
        load_dotenv(os.path.join(_repo_root_from(project), ".env"))


def load_jsonl(path):
    rows = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def read_prompt(prompts_dir, name, default=""):
    path = os.path.join(prompts_dir, name)
    if os.path.exists(path):
        with open(path) as f:
            return f.read()
    return default


def format_demo(text, label):
    return f"Review: {text}\nSentiment: {label}\n\n"


def parse_label(text, labels=None):
    """Read the last non-empty line first (chain-of-thought safe)."""
    lines = [ln.strip().lower() for ln in text.splitlines() if ln.strip()]
    candidates = ([lines[-1]] if lines else []) + [text.strip().lower()]
    label_set = [l.lower() for l in (labels or [])]
    for t in candidates:
        if label_set:
            present = [l for l in label_set if l in t]
            if len(present) == 1:
                return present[0]
        # generic two-class fallback
        has_pos, has_neg = "positive" in t, "negative" in t
        if has_pos and not has_neg:
            return "positive"
        if has_neg and not has_pos:
            return "negative"
    return "unknown"


def get_task_model(project, default="gpt-4.1-nano"):
    """Read llm.model from projects/<slug>_run.yaml without a yaml dependency."""
    slug = os.path.basename(os.path.normpath(project))
    cfg_path = os.path.join(_repo_root_from(project), "projects", f"{slug}_run.yaml")
    if os.path.exists(cfg_path):
        with open(cfg_path) as f:
            for line in f:
                m = re.match(r"\s*model:\s*[\"']?([^\"'\n]+)", line)
                if m:
                    return m.group(1).strip()
    return default


def write_report(out_dir, report):
    path = os.path.join(out_dir, "optimize_report.json")
    with open(path, "w") as f:
        f.write(json.dumps(report, indent=2) + "\n")
    return path


def run_current_prompt_on_train(rows, project, prompts_dir, model=None):
    """Classify TRAIN rows with the current prompts. Returns list of
    {input, expected, predicted, correct}. Used by hardness-aware methods."""
    from openai import OpenAI

    ensure_env(project)
    model = model or get_task_model(project)
    system = read_prompt(prompts_dir, "system.txt", "You are a classifier.")
    task = read_prompt(prompts_dir, "task.txt", "Classify: {text}")
    examples = read_prompt(prompts_dir, "examples.txt", "")
    labels = sorted({r["label"] for r in rows})
    client = OpenAI()

    out = []
    for r in rows:
        user = (examples + "\n" if examples else "") + task.format(text=r["text"])
        resp = client.chat.completions.create(
            model=model, temperature=0,
            messages=[{"role": "system", "content": system},
                      {"role": "user", "content": user}],
        )
        pred = parse_label(resp.choices[0].message.content, labels)
        out.append({"input": r["text"], "expected": r["label"],
                    "predicted": pred, "correct": pred == r["label"]})
    return out
