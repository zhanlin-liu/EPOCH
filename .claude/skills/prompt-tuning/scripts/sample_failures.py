#!/usr/bin/env python3
"""Sample failing rows from a TRAIN predictions file for prompt-tuning investigation.

Input is JSONL with rows containing at least: input, expected, predicted, correct.
Prints up to N failures (correct == false) for inspection. Deterministic: takes the
first N failures in file order so runs are reproducible.
"""
import argparse
import json


def sample_failures(path, n):
    failures = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            if not row.get("correct", True):
                failures.append(row)
            if len(failures) >= n:
                break
    return failures


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--preds", required=True, help="JSONL predictions file")
    ap.add_argument("--n", type=int, default=10)
    a = ap.parse_args()

    failures = sample_failures(a.preds, a.n)
    print(f"# {len(failures)} failure(s)\n")
    for i, row in enumerate(failures, 1):
        print(f"--- failure {i} ---")
        print(f"input:     {row.get('input')}")
        print(f"expected:  {row.get('expected')}")
        print(f"predicted: {row.get('predicted')}")
        print()


if __name__ == "__main__":
    main()
