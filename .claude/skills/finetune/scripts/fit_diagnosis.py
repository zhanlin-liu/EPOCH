#!/usr/bin/env python3
"""Classify model fit from train vs. eval metric for an EPOCH finetune round.

Higher-is-better metrics assumed (accuracy, precision, F1). For loss-style
metrics, pass --lower-is-better.
"""
import argparse


def diagnose(train, eval_, gap_threshold, low_threshold, lower_is_better):
    if lower_is_better:
        train, eval_ = -train, -eval_  # flip so higher == better
    gap = train - eval_
    if gap >= gap_threshold:
        return "OVERFIT", f"train-eval gap {gap:.3f} ≥ {gap_threshold}: ↑ regularization, ↓ epochs/lr"
    if train < low_threshold:
        return "UNDERFIT", f"train {train:.3f} < {low_threshold}: ↑ capacity/epochs, ↑ lr"
    return "OK", f"gap {gap:.3f} within tolerance; consider a different lever"


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--train", type=float, required=True)
    ap.add_argument("--eval", dest="eval_", type=float, required=True)
    ap.add_argument("--gap-threshold", type=float, default=0.08)
    ap.add_argument("--low-threshold", type=float, default=0.6)
    ap.add_argument("--lower-is-better", action="store_true")
    a = ap.parse_args()
    label, rec = diagnose(a.train, a.eval_, a.gap_threshold,
                          a.low_threshold, a.lower_is_better)
    print(f"{label}: {rec}")


if __name__ == "__main__":
    main()
