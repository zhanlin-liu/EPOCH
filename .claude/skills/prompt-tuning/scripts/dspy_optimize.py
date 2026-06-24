#!/usr/bin/env python3
"""DSPy prompt compilation (EPOCH prompt_tune). Standard optimizer contract.

Runs MIPROv2 or BootstrapFewShot over TRAIN, then flattens the compiled
instruction + demos into system.txt / examples.txt. TRAIN only.

Requires: dspy-ai  (uv add --project projects/<slug> dspy-ai)
"""
import argparse
import json
import os

from _contract import (ensure_env, load_jsonl, get_task_model, write_report,
                       format_demo)


def build_signature(dspy, labels):
    label_str = ", ".join(labels)

    class Classify(dspy.Signature):
        """Classify the text into one of the allowed labels."""
        text: str = dspy.InputField()
        label: str = dspy.OutputField(desc=f"one of: {label_str}")

    return Classify


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--project", required=True)
    ap.add_argument("--train", required=True)
    ap.add_argument("--prompts", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--config", default="{}")
    ap.add_argument("--seed", type=int, default=42)
    a = ap.parse_args()

    cfg = json.loads(a.config)
    optimizer_name = cfg.get("optimizer", "MIPROv2")
    auto = cfg.get("auto", "light")
    max_boot = int(cfg.get("max_bootstrapped_demos", 4))
    max_lab = int(cfg.get("max_labeled_demos", 4))
    optimizer_model = cfg.get("optimizer_model", "gpt-4.1-mini")

    ensure_env(a.project)
    try:
        import dspy
        from dspy.teleprompt import MIPROv2, BootstrapFewShot
    except ImportError:
        raise SystemExit("dspy not installed. Run: uv add --project <project> dspy-ai")

    task_model = get_task_model(a.project)
    dspy.configure(lm=dspy.LM(f"openai/{task_model}"))
    prompt_lm = dspy.LM(f"openai/{optimizer_model}")

    rows = load_jsonl(a.train)
    labels = sorted({r["label"] for r in rows})
    trainset = [dspy.Example(text=r["text"], label=r["label"]).with_inputs("text")
                for r in rows]

    signature = build_signature(dspy, labels)
    student = dspy.Predict(signature)

    def metric(example, pred, trace=None):
        return str(getattr(pred, "label", "")).strip().lower() == example.label.strip().lower()

    if optimizer_name == "BootstrapFewShot":
        tele = BootstrapFewShot(metric=metric, max_bootstrapped_demos=max_boot,
                                max_labeled_demos=max_lab)
        optimized = tele.compile(student=student, trainset=trainset)
    else:
        tele = MIPROv2(metric=metric, auto=auto, prompt_model=prompt_lm,
                       max_bootstrapped_demos=max_boot, max_labeled_demos=max_lab,
                       seed=a.seed)
        optimized = tele.compile(student=student, trainset=trainset,
                                 requires_permission_to_run=False)

    # Extract optimized instruction + demos from the (single) predictor.
    instruction, demos = None, []
    for _, predictor in optimized.named_predictors():
        try:
            instruction = predictor.signature.get_instructions()
        except Exception:
            instruction = getattr(predictor.signature, "instructions", None)
        demos = list(getattr(predictor, "demos", []) or [])
        break

    label_str = " or ".join(labels)
    system_text = (instruction or "Classify the text.").strip() + \
        f"\n\nRespond with only one word: {label_str}.\n"
    with open(os.path.join(a.out, "system.txt"), "w") as f:
        f.write(system_text)

    # Flatten demos into examples.txt (only those with text + label).
    demo_text = "Here are some examples:\n\n"
    n_demos = 0
    for d in demos:
        text = getattr(d, "text", None)
        label = getattr(d, "label", None)
        if text and label:
            demo_text += format_demo(text, label)
            n_demos += 1
    if n_demos:
        with open(os.path.join(a.out, "examples.txt"), "w") as f:
            f.write(demo_text)

    # Keep a clean single-word task template.
    with open(os.path.join(a.out, "task.txt"), "w") as f:
        f.write("Review: {text}\n\nSentiment:\n")

    write_report(a.out, {
        "method": "dspy",
        "config": cfg,
        "n_demos": n_demos,
        "n_llm_calls": None,  # DSPy manages its own call budget
        "internal_train_score": None,
        "notes": f"optimizer={optimizer_name}; flattened instruction + {n_demos} demos",
    })
    print(f"dspy: {optimizer_name} done; wrote system.txt + {n_demos} demos")


if __name__ == "__main__":
    main()
