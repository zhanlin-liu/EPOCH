#!/usr/bin/env python3
"""Confusion stats from a predictions file for an EPOCH rule_based round.

Input JSONL rows need boolean `expected` and `predicted`. Optional `rule`
field enables a per-rule breakdown with --by-rule.
"""
import argparse
import json
from collections import defaultdict


def tally(rows):
    c = {"tp": 0, "fp": 0, "fn": 0, "tn": 0}
    for r in rows:
        exp, pred = bool(r["expected"]), bool(r["predicted"])
        if exp and pred:
            c["tp"] += 1
        elif not exp and pred:
            c["fp"] += 1
        elif exp and not pred:
            c["fn"] += 1
        else:
            c["tn"] += 1
    return c


def prf(c):
    p = c["tp"] / (c["tp"] + c["fp"]) if (c["tp"] + c["fp"]) else 0.0
    r = c["tp"] / (c["tp"] + c["fn"]) if (c["tp"] + c["fn"]) else 0.0
    return p, r


def report(name, c):
    p, r = prf(c)
    print(f"[{name}] TP={c['tp']} FP={c['fp']} FN={c['fn']} TN={c['tn']} "
          f"| precision={p:.3f} recall={r:.3f}")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--preds", required=True)
    ap.add_argument("--by-rule", action="store_true")
    a = ap.parse_args()

    rows = []
    with open(a.preds) as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))

    report("overall", tally(rows))

    if a.by_rule:
        groups = defaultdict(list)
        for r in rows:
            groups[r.get("rule", "<none>")].append(r)
        print("\nPer rule:")
        for rule in sorted(groups):
            report(rule, tally(groups[rule]))


if __name__ == "__main__":
    main()
