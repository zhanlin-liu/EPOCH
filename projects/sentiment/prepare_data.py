"""Prepare a deterministic SST-2 subset for the EPOCH sentiment prompt_tune task.

Downloads SST-2 once, samples a fixed subset (seed 42), and writes local JSONL
splits. evaluate.py reads ONLY these local files.
"""
import json
import os
import random

from datasets import load_dataset

SEED = 42
TRAIN_PER_CLASS = 10
EVAL_PER_CLASS = 6
LABELS = {0: "negative", 1: "positive"}

HERE = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(HERE, "data")


def sample_split(rows, per_class):
    by_class = {0: [], 1: []}
    for r in rows:
        by_class[r["label"]].append(r)
    out = []
    rng = random.Random(SEED)
    for label, items in by_class.items():
        rng.shuffle(items)
        out.extend(items[:per_class])
    rng.shuffle(out)
    return out


def write_jsonl(path, rows):
    with open(path, "w") as f:
        for r in rows:
            f.write(json.dumps({"text": r["sentence"].strip(),
                                "label": LABELS[r["label"]]}) + "\n")


def main():
    os.makedirs(DATA_DIR, exist_ok=True)
    ds = load_dataset("stanfordnlp/sst2")
    # SST-2 test labels are hidden; use train for TRAIN subset, validation for EVAL.
    train_rows = sample_split(list(ds["train"]), TRAIN_PER_CLASS)
    eval_rows = sample_split(list(ds["validation"]), EVAL_PER_CLASS)
    write_jsonl(os.path.join(DATA_DIR, "train.jsonl"), train_rows)
    write_jsonl(os.path.join(DATA_DIR, "eval.jsonl"), eval_rows)
    print(f"wrote {len(train_rows)} train, {len(eval_rows)} eval rows to {DATA_DIR}")


if __name__ == "__main__":
    main()
