"""Prepare SST-2 subset for sentiment classification."""

import json
import random
from pathlib import Path

from datasets import load_dataset


def main():
    random.seed(42)
    data_dir = Path(__file__).parent / "data"
    data_dir.mkdir(exist_ok=True)

    # Load SST-2 from HuggingFace
    ds = load_dataset("glue", "sst2")

    # SST-2 labels: 0 = negative, 1 = positive
    label_map = {0: "negative", 1: "positive"}

    # Get all unique labels
    all_labels = sorted(label_map.keys())

    # Select num_classes (SST-2 has 2, config says 4 but we use all available)
    num_classes = min(4, len(all_labels))
    selected_labels = all_labels[:num_classes]

    train_samples_per_class = 10
    eval_samples_per_class = 6

    for split_name, split_key, samples_per_class in [
        ("train", "train", train_samples_per_class),
        ("eval", "validation", eval_samples_per_class),
    ]:
        # Group by label
        by_label = {l: [] for l in selected_labels}
        for example in ds[split_key]:
            label = example["label"]
            if label in selected_labels:
                by_label[label].append(example)

        # Sample per class
        records = []
        for label in selected_labels:
            pool = by_label[label]
            random.shuffle(pool)
            sampled = pool[:samples_per_class]
            for ex in sampled:
                records.append({
                    "text": ex["sentence"],
                    "label": label_map[ex["label"]],
                })

        # Shuffle final order
        random.shuffle(records)

        out_path = data_dir / f"{split_name}.jsonl"
        with open(out_path, "w") as f:
            for rec in records:
                f.write(json.dumps(rec) + "\n")

        # Summary
        label_counts = {}
        for rec in records:
            label_counts[rec["label"]] = label_counts.get(rec["label"], 0) + 1
        print(f"{split_name}: {len(records)} samples — {label_counts}")

    print(f"\nClasses: {[label_map[l] for l in selected_labels]}")
    print(f"Data saved to {data_dir}")


if __name__ == "__main__":
    main()
