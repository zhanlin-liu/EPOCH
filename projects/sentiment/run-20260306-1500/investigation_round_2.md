# Investigation Report — Round 2

**Run:** run-20260306-1500  
**Date:** 2026-06-18  
**Round:** 2  
**Investigator:** Claude (Sonnet 4.6)

---

## Current Metrics

| Split | Accuracy | Correct / Total |
|-------|----------|-----------------|
| TRAIN | 0.85     | 17 / 20         |

---

## Samples Analyzed

All 3 failures from the TRAIN split (lines 7, 10, 12 of train_preds.jsonl):

| # | Input | Expected | Predicted |
|---|-------|----------|-----------|
| 1 | "an era of theatrical comedy that , while past ," | positive | negative |
| 2 | "its opening" | positive | negative |
| 3 | "the film 's strength is n't in its details , but in the larger picture it paints - of a culture in conflict with itself , with the thin veneer of nationalism that covers our deepest , media-soaked fears ." | positive | negative |

---

## Patterns Identified

All three failures share the same root cause: **surface-level negative lexical anchoring overriding sentence-level or rhetorical intent.**

- **Failure 1 ("while past"):** The model treats "past" as loss/absence (negative) instead of nostalgic admiration. The SST fragment is a positive description of a bygone comedic era. The negative anchor is the single word "past."
- **Failure 2 ("its opening"):** A maximally ambiguous two-word fragment. With no surrounding context, the model defaults to negative. The annotated sentiment (positive) reflects that original review context praised the opening. The model cannot recover from the absence of positive signal and guesses negative.
- **Failure 3 ("strength is n't in its details, but in the larger picture"):** A contrast construction ("not X, but Y") where Y is praise. The surface words "is n't," "conflict with itself," "thin veneer," and "deepest ... fears" are all individually negative; the overall rhetorical direction is positive (the film achieves something bigger than its details). The model follows the negative lexical density rather than the contrastive structure.

**Dominant pattern:** The model does not perform explicit reasoning about sentence structure before labeling. It anchors to isolated negative-polarity words or defaults to negative on ambiguity, mishandling:
- Contrast constructions that end in praise ("not X, but Y — and Y is good")
- Nostalgic or past-referencing framing that is affectionate, not negative
- Short/ambiguous fragments where the only defensible approach is to seek the overall implied direction

This is a prompt-level gap: the current task prompt gives no guidance on how to handle surface-negative signals in otherwise positive contexts, and does not instruct the model to reason before deciding.

---

## Proposed Change

**File:** `projects/sentiment/src/prompts/task.txt`

**Current text:**
```
Classify the sentiment of the following movie review as either positive or negative.
Respond with only one word: positive or negative.

Review: {text}

Sentiment:
```

**Proposed text:**
```
Classify the sentiment of the following movie review as either positive or negative.

Important: Base your classification on the overall sentiment conveyed, not on individual negative-sounding words. Phrases like "the film's strength is not in X but in Y" or nostalgic references to something past can still express positive sentiment. If the text is ambiguous or very short, lean toward the sentiment most consistent with the overall tone or implication.

Respond with only one word: positive or negative.

Review: {text}

Sentiment:
```

**Rationale:**

The single addition is a guidance paragraph injected between the task instruction and the output format directive. It directly addresses the dominant failure pattern in three ways:

1. It explicitly warns the model not to over-weight isolated negative-sounding words — targeting failures 1 and 3.
2. It name-checks the "not X but Y" contrast construction as a known positive pattern — directly targeting failure 3, the hardest case.
3. It provides a tie-breaking heuristic for ambiguous/short fragments (lean toward the overall implied tone) — targeting failure 2.

The change is deliberately general: it does not hardcode the three specific failure examples, so it will generalize to similar constructions on unseen data. No EVAL content was used. The output format constraint ("Respond with only one word") is preserved unchanged so the eval script continues to parse correctly.

---

## Constraints Verified

- Only TRAIN split data examined (train_preds.jsonl).
- EVAL split (eval.jsonl) not read or referenced.
- Exactly one change proposed (task.txt instruction paragraph only).
- No few-shot examples added (keeps the prompt minimal; the guidance paragraph is the single lever).
