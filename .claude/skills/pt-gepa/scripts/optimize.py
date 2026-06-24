#!/usr/bin/env python3
"""GEPA reflective prompt evolution (EPOCH prompt_tune). Standard contract.

Collapses the current prompt into a seed system_prompt, evolves it over TRAIN
with gepa.optimize, and writes the best candidate into system.txt. TRAIN only.

Requires: gepa  (uv add --project projects/<slug> gepa)
Reference: https://github.com/gepa-ai/gepa
"""
import argparse
import json
import os
import random

from _contract import (ensure_env, load_jsonl, read_prompt, get_task_model,
                       write_report)

SINGLE_WORD_GUARD = "\n\nRespond with only one word: {labels}, on the final line."


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
    max_metric_calls = int(cfg.get("max_metric_calls", 150))
    reflection_model = cfg.get("reflection_model", "gpt-4.1-mini")
    val_fraction = float(cfg.get("val_fraction", 0.3))

    ensure_env(a.project)
    try:
        import gepa
    except ImportError:
        raise SystemExit("gepa not installed. Run: uv add --project <project> gepa")

    task_model = get_task_model(a.project)
    rows = load_jsonl(a.train)
    labels = sorted({r["label"] for r in rows})

    # Internal TRAIN split — never EVAL.
    rng = random.Random(a.seed)
    shuffled = rows[:]
    rng.shuffle(shuffled)
    n_val = max(1, int(len(shuffled) * val_fraction))
    valset = [{"input": r["text"], "answer": r["label"]} for r in shuffled[:n_val]]
    trainset = [{"input": r["text"], "answer": r["label"]} for r in shuffled[n_val:]]

    system = read_prompt(a.prompts, "system.txt", "You are a classifier.")
    task = read_prompt(a.prompts, "task.txt", "Classify: {text}")
    guard = SINGLE_WORD_GUARD.format(labels=" or ".join(labels))
    seed_candidate = {"system_prompt": (system.strip() + "\n\n" +
                                        task.replace("{text}", "the input").strip() + guard)}

    result = gepa.optimize(
        seed_candidate=seed_candidate,
        trainset=trainset,
        valset=valset,
        task_lm=f"openai/{task_model}",
        reflection_lm=f"openai/{reflection_model}",
        max_metric_calls=max_metric_calls,
        seed=a.seed,
    )

    best = result.best_candidate["system_prompt"].rstrip()
    if "only one word" not in best.lower():
        best += guard
    with open(os.path.join(a.out, "system.txt"), "w") as f:
        f.write(best + "\n")
    with open(os.path.join(a.out, "task.txt"), "w") as f:
        f.write("Review: {text}\n\nSentiment:\n")

    write_report(a.out, {
        "method": "gepa",
        "config": cfg,
        "n_demos": 0,
        "n_llm_calls": max_metric_calls,
        "internal_train_score": getattr(result, "best_score", None),
        "notes": f"evolved system_prompt; trainset={len(trainset)} valset={len(valset)}",
    })
    print("gepa: wrote evolved system.txt")


if __name__ == "__main__":
    main()
