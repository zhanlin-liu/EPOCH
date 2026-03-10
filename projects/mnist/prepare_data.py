"""Prepare MNIST subset for fast iteration.

Downloads the full MNIST dataset once, then creates a deterministic subset
with the configured number of classes and samples per class.
"""

import os
import random
import shutil
from pathlib import Path

import yaml
import torchvision
from PIL import Image


def main():
    project_dir = Path(__file__).parent
    config_path = project_dir.parent / "mnist_run.yaml"

    with open(config_path) as f:
        config = yaml.safe_load(f)

    seed = config["ml"]["seed"]
    subset = config["subset"]
    num_classes = subset["num_classes"]
    train_per_class = subset["train_samples_per_class"]
    eval_per_class = subset["eval_samples_per_class"]

    random.seed(seed)

    # Download full MNIST
    cache_dir = project_dir / "cache"
    train_dataset = torchvision.datasets.MNIST(root=str(cache_dir), train=True, download=True)
    test_dataset = torchvision.datasets.MNIST(root=str(cache_dir), train=False, download=True)

    # Select classes deterministically
    all_classes = list(range(10))
    random.shuffle(all_classes)
    selected_classes = sorted(all_classes[:num_classes])
    print(f"Selected classes: {selected_classes}")

    # Build index: class -> list of (image, label)
    train_by_class = {c: [] for c in selected_classes}
    for img, label in train_dataset:
        if label in train_by_class:
            train_by_class[label].append(img)

    eval_by_class = {c: [] for c in selected_classes}
    for img, label in test_dataset:
        if label in eval_by_class:
            eval_by_class[label].append(img)

    # Create output directories
    data_dir = project_dir / "data"
    if data_dir.exists():
        shutil.rmtree(data_dir)

    for split, by_class, per_class in [
        ("train", train_by_class, train_per_class),
        ("eval", eval_by_class, eval_per_class),
    ]:
        for cls, images in by_class.items():
            cls_dir = data_dir / split / f"class_{cls}"
            cls_dir.mkdir(parents=True, exist_ok=True)

            random.shuffle(images)
            selected = images[:per_class]
            for i, img in enumerate(selected):
                # Convert to RGB for MobileNetV2 (expects 3 channels)
                img_rgb = img.convert("RGB")
                img_rgb.save(cls_dir / f"img_{i:04d}.jpg")

            print(f"  {split}/class_{cls}: {len(selected)} images")

    print(f"\nData prepared at {data_dir}")
    print(f"  Train: {num_classes} classes x {train_per_class} = {num_classes * train_per_class}")
    print(f"  Eval:  {num_classes} classes x {eval_per_class} = {num_classes * eval_per_class}")


if __name__ == "__main__":
    main()
