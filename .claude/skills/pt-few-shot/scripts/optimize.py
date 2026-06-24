#!/usr/bin/env python3
"""Few-shot demo selection (EPOCH prompt_tune). Standard optimizer contract.

Selects K balanced demos from TRAIN and writes examples.txt. Optional
"hard-balanced" selection runs the current prompt over TRAIN to prefer
currently-misclassified examples. TRAIN only — never reads eval.jsonl.
"""
import argparse
import json
import os
import random
from collections import defaultdict

from _contract import (load_jsonl, read_prompt, write_report, format_demo,
                       run_current_prompt_on_train)


def select_balanced(rows, k, seed):
    by_class = defaultdict(list)
    for r in rows:
        by_class[r["label"]].append(r)
    rng = random.Random(seed)
    classes = sorted(by_class)
    per = max(1, k // len(classes))
    picked = []
    for c in classes:
        items = by_class[c][:]
        rng.shuffle(items)
        picked.extend(items[:per])
    rng.shuffle(picked)
    return picked[:k]


def select_hard_balanced(rows, k, seed, project, prompts_dir):
    preds = run_current_prompt_on_train(rows, project, prompts_dir)
    hard = [r for r, p in zip(rows, preds) if not p["correct"]]
    easy = [r for r, p in zip(rows, preds) if p["correct"]]
    # Prefer hard, balance classes, top up with easy.
    chosen = select_balanced(hard, k, seed)
    if len(chosen) < k:
        chosen += select_balanced(easy, k - len(chosen), seed)
    return chosen[:k], len(rows)


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
    k = int(cfg.get("k", 4))
    selection = cfg.get("selection", "balanced")
    rows = load_jsonl(a.train)

    n_calls = 0
    if selection == "hard-balanced":
        demos, n_calls = select_hard_balanced(rows, k, a.seed, a.project, a.prompts)
    else:
        demos = select_balanced(rows, k, a.seed)

    examples_text = "Here are some examples:\n\n" + "".join(
        format_demo(d["text"], d["label"]) for d in demos
    )
    out_path = os.path.join(a.out, "examples.txt")
    with open(out_path, "w") as f:
        f.write(examples_text)

    write_report(a.out, {
        "method": "few-shot",
        "config": cfg,
        "n_demos": len(demos),
        "n_llm_calls": n_calls,
        "internal_train_score": None,
        "notes": f"selection={selection}; wrote {out_path}",
    })
    print(f"few-shot: wrote {len(demos)} demos to {out_path}")


if __name__ == "__main__":
    main()
