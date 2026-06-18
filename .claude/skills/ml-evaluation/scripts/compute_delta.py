#!/usr/bin/env python3
"""Compute per-metric deltas between two EPOCH metrics files.

Each input is a flat JSON object of metric_name -> value. Output is a JSON
object of metric_name -> {baseline, proposed, delta}.
"""
import argparse
import json


def compute_delta(baseline, proposed):
    keys = sorted(set(baseline) | set(proposed))
    out = {}
    for k in keys:
        b = baseline.get(k)
        p = proposed.get(k)
        delta = None
        if isinstance(b, (int, float)) and isinstance(p, (int, float)):
            delta = p - b
        out[k] = {"baseline": b, "proposed": p, "delta": delta}
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--baseline", required=True)
    ap.add_argument("--proposed", required=True)
    ap.add_argument("--out", default=None, help="write JSON here; else stdout")
    a = ap.parse_args()

    with open(a.baseline) as f:
        baseline = json.load(f)
    with open(a.proposed) as f:
        proposed = json.load(f)

    result = compute_delta(baseline, proposed)
    text = json.dumps(result, indent=2)
    if a.out:
        with open(a.out, "w") as f:
            f.write(text + "\n")
        print(f"wrote {a.out}")
    else:
        print(text)


if __name__ == "__main__":
    main()
