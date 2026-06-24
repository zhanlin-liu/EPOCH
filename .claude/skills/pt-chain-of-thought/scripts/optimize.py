#!/usr/bin/env python3
"""Chain-of-thought prompt reformat (EPOCH prompt_tune). Standard contract.

Deterministic: rewrites task.txt to reason briefly, then output one label word
on the final line. No LLM calls. TRAIN only (reads labels for the instruction).
"""
import argparse
import json
import os

from _contract import load_jsonl, read_prompt, write_report


def build_task(labels, max_sentences, final_line_hint):
    label_str = " or ".join(labels) if labels else "the correct label"
    return (
        f"Classify the sentiment of the following movie review as either {label_str}.\n\n"
        f"Think step by step: in 1-{max_sentences} sentences, identify what the review is "
        f"expressing — consider the overall rhetorical direction, any contrast structures "
        f'(e.g. "not X but Y"), and the implied attitude. Then, on its own final line, '
        f"output exactly one word: {label_str}.\n\n"
        f"Review: {{text}}\n\n"
        f"{final_line_hint}\n"
    )


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
    max_sentences = int(cfg.get("max_sentences", 3))
    hint = cfg.get("final_line_hint", "Reasoning and sentiment:")

    rows = load_jsonl(a.train)
    labels = sorted({r["label"] for r in rows})
    new_task = build_task(labels, max_sentences, hint)

    # sanity: placeholder preserved
    assert "{text}" in new_task, "task.txt must keep the {text} placeholder"

    out_path = os.path.join(a.out, "task.txt")
    with open(out_path, "w") as f:
        f.write(new_task)

    write_report(a.out, {
        "method": "chain-of-thought",
        "config": cfg,
        "n_demos": 0,
        "n_llm_calls": 0,
        "internal_train_score": None,
        "notes": f"rewrote {out_path}; final-line single-word contract preserved",
    })
    print(f"chain-of-thought: rewrote {out_path}")


if __name__ == "__main__":
    main()
