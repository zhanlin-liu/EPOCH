#!/usr/bin/env python3
"""LLM-driven instruction refinement (EPOCH prompt_tune). Standard contract.

Runs the current prompt over TRAIN to collect failures, then asks an optimizer
model to rewrite system.txt/task.txt. Preserves {text} and the single-word
final-line output contract. TRAIN only.
"""
import argparse
import json
import os

from _contract import (ensure_env, load_jsonl, read_prompt, write_report,
                       run_current_prompt_on_train)

REWRITE_SYS = (
    "You are an expert prompt engineer. You improve a classification prompt so it makes "
    "fewer mistakes, WITHOUT overfitting to specific examples. You must keep the prompt "
    "general."
)


def build_rewrite_request(system, task, failures, labels):
    fail_lines = "\n".join(
        f'- text: "{f["input"]}" | expected: {f["expected"]} | predicted: {f["predicted"]}'
        for f in failures
    )
    return f"""Here is the current prompt for a {"/".join(labels)} text classifier.

=== system.txt ===
{system}

=== task.txt ===
{task}

The task.txt MUST contain the literal placeholder {{text}} where the input goes, and the
prompt MUST instruct the model to output the final label as a single word on the final line.

These TRAIN examples are currently misclassified:
{fail_lines}

Rewrite the prompt to fix the general weakness these reveal. Return STRICT JSON:
{{"system": "<new system.txt>", "task": "<new task.txt, includes {{text}} and single-word final-line instruction>"}}
Do not include any text outside the JSON.
"""


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--project", required=True)
    ap.add_argument("--train", required=True)
    ap.add_argument("--prompts", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--config", default="{}")
    ap.add_argument("--seed", type=int, default=42)
    a = ap.parse_args()

    cfg = json.loads(a.config)
    optimizer_model = cfg.get("optimizer_model", "gpt-4.1-mini")
    max_failures = int(cfg.get("max_failures", 8))

    rows = load_jsonl(a.train)
    labels = sorted({r["label"] for r in rows})
    system = read_prompt(a.prompts, "system.txt", "You are a classifier.")
    task = read_prompt(a.prompts, "task.txt", "Classify: {text}")

    preds = run_current_prompt_on_train(rows, a.project, a.prompts)
    failures = [p for p in preds if not p["correct"]][:max_failures]
    n_calls = len(rows)  # from running current prompt over TRAIN

    ensure_env(a.project)
    from openai import OpenAI
    client = OpenAI()
    resp = client.chat.completions.create(
        model=optimizer_model, temperature=0,
        response_format={"type": "json_object"},
        messages=[{"role": "system", "content": REWRITE_SYS},
                  {"role": "user", "content": build_rewrite_request(system, task, failures, labels)}],
    )
    n_calls += 1
    out = json.loads(resp.choices[0].message.content)
    new_system, new_task = out["system"], out["task"]

    # contract guards
    if "{text}" not in new_task:
        raise SystemExit("refusing to write: new task.txt dropped the {text} placeholder")

    with open(os.path.join(a.out, "system.txt"), "w") as f:
        f.write(new_system.rstrip() + "\n")
    with open(os.path.join(a.out, "task.txt"), "w") as f:
        f.write(new_task.rstrip() + "\n")

    write_report(a.out, {
        "method": "system-refinement",
        "config": cfg,
        "n_demos": 0,
        "n_llm_calls": n_calls,
        "internal_train_score": round(1 - len(failures) / max(1, len(rows)), 4),
        "notes": f"rewrote system.txt + task.txt from {len(failures)} TRAIN failures",
    })
    print(f"system-refinement: rewrote prompts ({n_calls} LLM calls)")


if __name__ == "__main__":
    main()
