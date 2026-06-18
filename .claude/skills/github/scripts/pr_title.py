#!/usr/bin/env python3
"""Build an EPOCH PR title from round metrics.

Format: [Round N] (eval: X.XX -> Y.YY | train: X.XX -> Y.YY) <summary>
"""
import argparse


def build_title(round_n, eval_old, eval_new, summary,
                train_old=None, train_new=None):
    metrics = f"eval: {eval_old:.2f} → {eval_new:.2f}"
    if train_old is not None and train_new is not None:
        metrics += f" | train: {train_old:.2f} → {train_new:.2f}"
    return f"[Round {round_n}] ({metrics}) {summary}"


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--round", type=int, required=True)
    p.add_argument("--eval-old", type=float, required=True)
    p.add_argument("--eval-new", type=float, required=True)
    p.add_argument("--train-old", type=float, default=None)
    p.add_argument("--train-new", type=float, default=None)
    p.add_argument("--summary", required=True)
    a = p.parse_args()
    print(build_title(a.round, a.eval_old, a.eval_new, a.summary,
                      a.train_old, a.train_new))


if __name__ == "__main__":
    main()
