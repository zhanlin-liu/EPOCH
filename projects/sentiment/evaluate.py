"""Evaluate sentiment classification using LLM prompts."""

import asyncio
import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from openai import AsyncOpenAI

load_dotenv()

PROJECT_DIR = Path(__file__).parent
PROMPTS_DIR = PROJECT_DIR / "src" / "prompts"
DATA_DIR = PROJECT_DIR / "data"

CONCURRENCY = 12
MODEL = "gpt-4.1-nano"


def load_prompts():
    system_prompt = (PROMPTS_DIR / "system.txt").read_text().strip()
    task_template = (PROMPTS_DIR / "task.txt").read_text().strip()

    examples_path = PROMPTS_DIR / "examples.txt"
    if examples_path.exists():
        examples = examples_path.read_text().strip()
        task_template = examples + "\n\n" + task_template

    return system_prompt, task_template


def load_data(split: str):
    file_map = {"train": "train.jsonl", "eval": "eval.jsonl"}
    path = DATA_DIR / file_map[split]
    records = []
    with open(path) as f:
        for line in f:
            records.append(json.loads(line))
    return records


def normalize_label(response: str) -> str:
    text = response.strip().lower()
    if "positive" in text:
        return "positive"
    if "negative" in text:
        return "negative"
    return text


async def classify_one(client, semaphore, system_prompt, task_template, record, index):
    prompt = task_template.replace("{text}", record["text"])
    async with semaphore:
        try:
            resp = await client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt},
                ],
                temperature=0,
                max_tokens=16,
            )
            raw = resp.choices[0].message.content.strip()
            predicted = normalize_label(raw)
        except Exception as e:
            raw = str(e)
            predicted = "error"

    return {
        "index": index,
        "text": record["text"],
        "expected": record["label"],
        "predicted": predicted,
        "raw_response": raw,
        "correct": predicted == record["label"],
    }


async def run_eval(split: str):
    system_prompt, task_template = load_prompts()
    records = load_data(split)

    client = AsyncOpenAI()
    semaphore = asyncio.Semaphore(CONCURRENCY)

    tasks = [
        classify_one(client, semaphore, system_prompt, task_template, rec, i)
        for i, rec in enumerate(records)
    ]
    results = await asyncio.gather(*tasks)

    correct = sum(1 for r in results if r["correct"])
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

    asyncio.run(run_eval(split))


if __name__ == "__main__":
    main()
