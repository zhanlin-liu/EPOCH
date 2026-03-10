"""Prepare Iris dataset with train/eval split."""

import json
import random
from pathlib import Path

from sklearn.datasets import load_iris


def main():
    random.seed(42)
    data_dir = Path(__file__).parent / "data"
    data_dir.mkdir(exist_ok=True)

    iris = load_iris()
    feature_names = iris.feature_names
    target_names = list(iris.target_names)

    # Group by class
    by_class = {i: [] for i in range(3)}
    for features, label in zip(iris.data, iris.target):
        by_class[int(label)].append({
            "sepal_length": float(features[0]),
            "sepal_width": float(features[1]),
            "petal_length": float(features[2]),
            "petal_width": float(features[3]),
            "label": target_names[int(label)],
        })

    # Shuffle each class
    for cls in by_class:
        random.shuffle(by_class[cls])

    # Split: 35 train, 15 eval per class
    train_per_class = 35
    eval_per_class = 15

    train_records = []
    eval_records = []
    for cls in sorted(by_class.keys()):
        samples = by_class[cls]
        train_records.extend(samples[:train_per_class])
        eval_records.extend(samples[train_per_class:train_per_class + eval_per_class])

    random.shuffle(train_records)
    random.shuffle(eval_records)

    for split_name, records in [("train", train_records), ("eval", eval_records)]:
        out_path = data_dir / f"{split_name}.jsonl"
        with open(out_path, "w") as f:
            for rec in records:
                f.write(json.dumps(rec) + "\n")
        label_counts = {}
        for rec in records:
            label_counts[rec["label"]] = label_counts.get(rec["label"], 0) + 1
        print(f"{split_name}: {len(records)} samples — {label_counts}")

    print(f"\nFeatures: {feature_names}")
    print(f"Classes: {target_names}")
    print(f"Data saved to {data_dir}")


if __name__ == "__main__":
    main()
