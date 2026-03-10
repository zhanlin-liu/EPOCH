"""Train and evaluate MobileNetV2 on MNIST subset.

Usage:
    python projects/mnist/evaluate.py train   # Train + evaluate on TRAIN split
    python projects/mnist/evaluate.py eval    # Train + evaluate on EVAL split

Reads tunable hyperparameters from hyperparams.json.
Reads fixed parameters from mnist_run.yaml.
"""

import json
import random
import sys
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
import yaml
from torch.utils.data import DataLoader
from torchvision import models, transforms
from torchvision.datasets import ImageFolder


def set_seed(seed: int):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False


def get_device():
    if torch.cuda.is_available():
        return torch.device("cuda")
    elif torch.backends.mps.is_available():
        return torch.device("mps")
    return torch.device("cpu")


def load_config():
    project_dir = Path(__file__).parent
    config_path = project_dir.parent / "mnist_run.yaml"
    with open(config_path) as f:
        return yaml.safe_load(f)


def load_hyperparams():
    project_dir = Path(__file__).parent
    hp_path = project_dir / "hyperparams.json"
    with open(hp_path) as f:
        hp = json.load(f)
    # Remove metadata
    return {k: v for k, v in hp.items() if k != "metadata"}


def build_model(num_classes: int, device: torch.device):
    model = models.mobilenet_v2(weights=models.MobileNet_V2_Weights.IMAGENET1K_V1)
    # Freeze all layers except classifier
    for param in model.parameters():
        param.requires_grad = False
    model.classifier[1] = nn.Linear(model.last_channel, num_classes)
    return model.to(device)


def build_optimizer(model, hp: dict):
    name = hp["optimizer"]
    lr = hp["learning_rate"]
    params = filter(lambda p: p.requires_grad, model.parameters())
    if name == "adam":
        return torch.optim.Adam(params, lr=lr)
    elif name == "adamw":
        return torch.optim.AdamW(params, lr=lr)
    elif name == "sgd":
        return torch.optim.SGD(params, lr=lr, momentum=0.9)
    else:
        raise ValueError(f"Unknown optimizer: {name}")


def get_transform():
    return transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])


def train_epoch(model, loader, criterion, optimizer, device):
    model.train()
    total_loss = 0.0
    correct = 0
    total = 0
    for images, labels in loader:
        images, labels = images.to(device), labels.to(device)
        optimizer.zero_grad()
        outputs = model(images)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()
        total_loss += loss.item() * images.size(0)
        _, predicted = outputs.max(1)
        correct += predicted.eq(labels).sum().item()
        total += labels.size(0)
    return total_loss / total, correct / total


def evaluate(model, loader, criterion, device):
    model.eval()
    total_loss = 0.0
    correct = 0
    total = 0
    with torch.no_grad():
        for images, labels in loader:
            images, labels = images.to(device), labels.to(device)
            outputs = model(images)
            loss = criterion(outputs, labels)
            total_loss += loss.item() * images.size(0)
            _, predicted = outputs.max(1)
            correct += predicted.eq(labels).sum().item()
            total += labels.size(0)
    return total_loss / total, correct / total


def main():
    if len(sys.argv) != 2 or sys.argv[1] not in ("train", "eval"):
        print("Usage: python evaluate.py [train|eval]")
        sys.exit(1)

    split = sys.argv[1]
    config = load_config()
    hp = load_hyperparams()
    seed = config["ml"]["seed"]
    max_epochs = config["ml"]["max_train_epochs"]
    num_classes = config["subset"]["num_classes"]

    set_seed(seed)
    device = get_device()
    print(f"Device: {device}")
    print(f"Hyperparams: {hp}")
    print(f"Max epochs: {max_epochs}, Seed: {seed}")

    project_dir = Path(__file__).parent
    data_dir = project_dir / "data"

    train_dataset = ImageFolder(str(data_dir / "train"), transform=get_transform())
    eval_dataset = ImageFolder(str(data_dir / "eval"), transform=get_transform())

    g = torch.Generator().manual_seed(seed)
    train_loader = DataLoader(train_dataset, batch_size=16, shuffle=True, generator=g)
    eval_loader = DataLoader(eval_dataset, batch_size=16, shuffle=False)

    model = build_model(num_classes, device)
    optimizer = build_optimizer(model, hp)
    criterion = nn.CrossEntropyLoss()

    # Train
    print(f"\nTraining for {max_epochs} epochs...")
    for epoch in range(1, max_epochs + 1):
        train_loss, train_acc = train_epoch(model, train_loader, criterion, optimizer, device)
        print(f"  Epoch {epoch}: loss={train_loss:.4f}, acc={train_acc:.4f}")

    # Evaluate on requested split
    if split == "train":
        loss, acc = evaluate(model, train_loader, criterion, device)
        print(f"\nTRAIN metrics: accuracy={acc:.4f}, loss={loss:.4f}")
    else:
        loss, acc = evaluate(model, eval_loader, criterion, device)
        print(f"\nEVAL metrics: accuracy={acc:.4f}, loss={loss:.4f}")

    # Also compute both for metrics file
    train_loss, train_acc = evaluate(model, train_loader, criterion, device)
    eval_loss, eval_acc = evaluate(model, eval_loader, criterion, device)

    metrics = {
        "train_accuracy": round(train_acc, 4),
        "train_loss": round(train_loss, 4),
        "eval_accuracy": round(eval_acc, 4),
        "eval_loss": round(eval_loss, 4),
        "train_eval_gap": round(abs(train_acc - eval_acc), 4),
        "hyperparams": hp,
        "config": {
            "seed": seed,
            "max_epochs": max_epochs,
            "num_classes": num_classes,
        },
    }

    # Save metrics
    run_dirs = sorted((project_dir).glob("run-*"))
    if run_dirs:
        out_path = run_dirs[-1] / f"{split}_metrics.json"
    else:
        out_path = project_dir / f"{split}_metrics.json"

    with open(out_path, "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"\nMetrics saved to {out_path}")
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
