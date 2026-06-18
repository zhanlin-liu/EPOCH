# Investigation Report — Round 2 Retry 1

**Run:** run-20260306-1500  
**Date:** 2026-06-18  
**Round:** 2 Retry 1  
**Retry strategy:** REFINE — chain-of-thought output format  
**Investigator:** Claude (Sonnet 4.6)

---

## Current Metrics

| Split | Accuracy | Correct / Total |
|-------|----------|-----------------|
| TRAIN | 0.85     | 17 / 20         |
| EVAL (baseline, locked) | 0.8333 | 10 / 12 |

Round 2 delta on EVAL: 0.000 (rejected).

---

## What Was Tried in Round 2 (Rejected)

A guidance paragraph was injected into task.txt instructing the model to base classification on overall sentiment rather than individual negative-sounding words, naming the "not X but Y" contrast construction and providing a tie-breaker heuristic for short/ambiguous inputs.

Result: no lift on EVAL. The heuristic instructions were too abstract — the model received the guidance but had no mechanism to reason through ambiguous cases before committing to a label. Giving a declarative rule does not force the model to apply it.

---

## Samples Analyzed (TRAIN only)

All 3 failures from train_preds.jsonl (the same three that existed at Round 2, confirming the Round 2 prompt did not fix them on TRAIN either):

| # | Input | Expected | Predicted |
|---|-------|----------|-----------|
| 1 | "an era of theatrical comedy that , while past ," | positive | negative |
| 2 | "its opening" | positive | negative |
| 3 | "the film 's strength is n't in its details , but in the larger picture it paints - of a culture in conflict with itself , with the thin veneer of nationalism that covers our deepest , media-soaked fears ." | positive | negative |

---

## Pattern Analysis

All three failures share the same structural root cause: **the model anchors to surface-level negative-polarity tokens without performing any intermediate reasoning about rhetorical structure or implication before producing the label.**

- Failure 1: The single word "past" triggers a negative association (loss, absence). The nostalgic/affectionate framing around it is ignored.
- Failure 2: No positive signal exists in the fragment. With zero positive tokens, the model defaults to negative. The correct label requires inferring from context that film openings are typically praised when cited in short-form.
- Failure 3: The contrastive frame "strength is n't in X, but in Y" nominally praises Y (the larger picture). But "isn't," "conflict with itself," "thin veneer," and "fears" are all individually negative, creating a high density of negative tokens that overwhelms the contrastive intent.

**Why Round 2 failed:** A declarative instruction ("base on overall sentiment") does not alter the model's internal computation path; it adds a constraint but not a reasoning procedure. The model processes the tokens and produces a label — the rule is available but not operationalized.

**Dominant hypothesis for Retry 1:** Forcing the model to output an explicit reasoning step before the label requires it to construct an intermediate representation of the text's rhetorical direction. This externalized reasoning acts as a self-correction mechanism: the model must articulate whether the text is praising or criticizing before selecting the label, making it harder to silently anchor to surface negatives.

---

## Proposed Change

**File:** `projects/sentiment/src/prompts/task.txt`

**One change only:** Replace the full contents of task.txt with a chain-of-thought format that instructs a brief (1–3 sentence) reasoning step before the final label, and requires the final line to be exactly one word.

**Proposed full contents of task.txt:**

```
Classify the sentiment of the following movie review as either positive or negative.

Think step by step: in 1-3 sentences, identify what the review is expressing — consider the overall rhetorical direction, any contrast structures, and the implied attitude toward the subject. Then, on its own final line, output exactly one word: positive or negative.

Review: {text}

Reasoning and sentiment:
```

**Rationale:**

The chain-of-thought format compels the model to produce an intermediate reasoning trace before committing to a label. This operationalizes what the Round 2 heuristic only declared: the model must now articulate the rhetorical direction of the text (praise vs. criticism, contrast structure, overall implied attitude) in natural language before selecting the label. For failure cases like contrast constructions ("not X but Y") and nostalgic framing, this reasoning step is likely to surface the positive direction before the label is written, reducing the chance that surface negative tokens dominate. The instruction is deliberately general — it names reasoning strategies (overall rhetorical direction, contrast structures, implied attitude) without hardcoding any of the three specific failure inputs. The final-line single-word constraint preserves compatibility with the evaluator's parser.

---

## Constraints Verified

- Only TRAIN split data examined (train_preds.jsonl, 20 samples, 3 failures).
- EVAL split (eval.jsonl) not read or referenced.
- Exactly one change proposed: full replacement of task.txt with CoT format.
- The "lean toward overall tone" heuristic from Round 2 is NOT carried forward.
- Parser compatibility preserved: final output line is exactly one word (positive or negative).
