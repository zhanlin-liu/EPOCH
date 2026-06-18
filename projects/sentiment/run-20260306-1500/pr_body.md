# Round 2 Review — sentiment / run-20260306-1500

## Metrics Table

| Metric         | Baseline | Proposed | Delta  | Threshold | Status |
|----------------|----------|----------|--------|-----------|--------|
| eval_accuracy  | 0.8333   | 0.8333   | 0.0000 | +0.02     | FAIL   |

## EVAL Leakage Check

PASS. The investigation report explicitly confirms only `train_preds.jsonl` (TRAIN split) was read. `eval.jsonl` was not opened or referenced at any point. The proposed prompt change was derived solely from TRAIN-split failure analysis.

## Verdict: REJECT

The primary metric (eval_accuracy) did not improve. The delta is 0.0000 against a required minimum delta of 0.02. The acceptance threshold is not met.

## Root Cause

The guidance paragraph added to `task.txt` was logically well-reasoned and correctly targeted the three identified TRAIN failure patterns (surface-negative lexical anchoring, nostalgic-framing misclassification, and short-fragment defaulting to negative). However, the intervention produced no measurable lift on the EVAL split. Two likely explanations:

1. **EVAL failures are different in kind.** The 2 EVAL errors (10/12 correct) may not share the same surface-negative / contrast-construction pattern that was diagnosed on TRAIN. General guidance that addresses TRAIN failures may simply not fire on the EVAL examples that are still wrong.
2. **The model already handles the guidance implicitly.** The underlying model (Sonnet 4.6) may already apply chain-of-thought-style hedging internally; the added paragraph may not shift its probability mass enough to flip any borderline EVAL predictions.

The change was not harmful (no regression), but it was also not effective.

## Retry Recommendation: REFINE

Do NOT revert. The prompt is not worse, and the TRAIN accuracy was already 0.85; reverting to the bare prompt risks losing that signal on future rounds.

For Round 3, try the following instead of (or in addition to) the current guidance paragraph:

1. **Inspect EVAL predictions first.** Read `eval_preds.jsonl` (round 2 output) and identify exactly which 2 examples are still wrong. The retry hypothesis must be grounded in EVAL failure patterns, not extrapolated from TRAIN alone.
2. **Add explicit chain-of-thought before the label.** Change the output format to require a one-sentence reasoning step before the final label (e.g., "Reasoning: ... Label: positive/negative"). This forces the model to surface its intermediate reasoning, which is the mechanism that the current guidance paragraph only hints at.
3. **Do not add few-shot examples** unless the EVAL failures are clearly a pattern the model has never seen; few-shot risks overfitting to specific surface forms.
4. **Do not repeat** the "lean toward overall tone" heuristic in a new form — it was already present in round 2 and did not move the needle.
