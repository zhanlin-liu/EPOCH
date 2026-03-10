"""Evaluate rule-based Iris classifier."""

import json
import os
import sys
from pathlib import Path

from rules.rules import classify

PROJECT_DIR = Path(__file__).parent
DATA_DIR = PROJECT_DIR / "data"


def load_data(split: str):
    path = DATA_DIR / f"{split}.jsonl"
    records = []
    with open(path) as f:
        for line in f:
            records.append(json.loads(line))
    return records


def run_eval(split: str):
    records = load_data(split)

    results = []
    correct = 0
    for i, rec in enumerate(records):
        predicted = classify(rec)
        is_correct = predicted == rec["label"]
        if is_correct:
            correct += 1
        results.append({
            "index": i,
            "features": {
                "sepal_length": rec["sepal_length"],
                "sepal_width": rec["sepal_width"],
                "petal_length": rec["petal_length"],
                "petal_width": rec["petal_width"],
            },
            "expected": rec["label"],
            "predicted": predicted,
            "correct": is_correct,
        })

    total = len(results)
    accuracy = correct / total if total > 0 else 0.0
    failures = [r for r in results if not r["correct"]]

    # Save detailed results
    run_id = os.environ.get("EPOCH_RUN_ID", "latest")
    output_dir = PROJECT_DIR / run_id
    output_dir.mkdir(exist_ok=True)
    with open(output_dir / f"{split}_results.json", "w") as f:
        json.dump(results, f, indent=2)

    metrics = {
        f"{split}_accuracy": round(accuracy, 4),
        f"{split}_correct": correct,
        f"{split}_total": total,
        f"{split}_failures": len(failures),
    }

    print(json.dumps(metrics))
    return metrics


def main():
    if len(sys.argv) < 2:
        print("Usage: python evaluate.py <train|eval>", file=sys.stderr)
        sys.exit(1)

    split = sys.argv[1]
    if split not in ("train", "eval"):
        print(f"Invalid split: {split}. Use 'train' or 'eval'.", file=sys.stderr)
        sys.exit(1)

    run_eval(split)


if __name__ == "__main__":
    main()
