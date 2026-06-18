"""Evaluate the sentiment prompt on a data split via gpt-4.1-nano (async).

Usage:
    python evaluate.py train
    python evaluate.py eval

Reads prompts from src/prompts/ and data from data/<split>.jsonl. Prints a
metrics JSON to stdout. For the TRAIN split, also writes data/train_preds.jsonl
(input/expected/predicted/correct) for the investigator.
"""
import asyncio
import json
import os
import sys

from dotenv import load_dotenv
from openai import AsyncOpenAI

HERE = os.path.dirname(os.path.abspath(__file__))
PROMPT_DIR = os.path.join(HERE, "src", "prompts")
DATA_DIR = os.path.join(HERE, "data")

# Load OPENAI_API_KEY from repo-root .env (two levels up: projects/sentiment -> repo).
load_dotenv(os.path.join(HERE, "..", "..", ".env"))

MODEL = "gpt-4.1-nano"
CONCURRENCY = 12


def read_prompt(name):
    with open(os.path.join(PROMPT_DIR, name)) as f:
        return f.read()


def read_split(split):
    rows = []
    with open(os.path.join(DATA_DIR, f"{split}.jsonl")) as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def parse_label(text):
    t = text.strip().lower()
    has_pos = "positive" in t
    has_neg = "negative" in t
    if has_pos and not has_neg:
        return "positive"
    if has_neg and not has_pos:
        return "negative"
    # fall back to first token
    first = t.split()[0] if t.split() else ""
    if first.startswith("pos"):
        return "positive"
    if first.startswith("neg"):
        return "negative"
    return "unknown"


async def classify(client, system, task, row, sem):
    async with sem:
        resp = await client.chat.completions.create(
            model=MODEL,
            temperature=0,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": task.format(text=row["text"])},
            ],
        )
    pred = parse_label(resp.choices[0].message.content)
    return {
        "input": row["text"],
        "expected": row["label"],
        "predicted": pred,
        "correct": pred == row["label"],
    }


async def run(split):
    system = read_prompt("system.txt")
    task = read_prompt("task.txt")
    rows = read_split(split)
    client = AsyncOpenAI()
    sem = asyncio.Semaphore(CONCURRENCY)
    results = await asyncio.gather(
        *(classify(client, system, task, r, sem) for r in rows)
    )
    correct = sum(1 for r in results if r["correct"])
    total = len(results)
    accuracy = correct / total if total else 0.0

    if split == "train":
        with open(os.path.join(DATA_DIR, "train_preds.jsonl"), "w") as f:
            for r in results:
                f.write(json.dumps(r) + "\n")

    print(json.dumps({
        "split": split,
        "accuracy": round(accuracy, 4),
        "correct": correct,
        "total": total,
    }))


def main():
    split = sys.argv[1] if len(sys.argv) > 1 else "eval"
    if split not in ("train", "eval"):
        print(f"unknown split: {split}", file=sys.stderr)
        sys.exit(2)
    asyncio.run(run(split))


if __name__ == "__main__":
    main()
