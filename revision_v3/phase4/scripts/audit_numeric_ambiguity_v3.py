import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(
    0,
    "revision_v3/phase4/scripts",
)

from score_correctness_v3 import (
    numeric_mentions,
    _explicit_numeric_answer_segment,
)


ROOT = Path(
    "revision_v3/phase4/data"
)

OUT = Path(
    "revision_v3/phase4/results/"
    "numeric_ambiguity_audit_v3.json"
)

MODELS = [
    "qwen25_3b",
    "qwen25_7b",
    "mistral_7b",
    "phi35_mini",
    "granite33_8b",
    "falcon3_7b",
]


print("=" * 112)
print(
    "DANGERMAP-RAG PHASE 4C-3: "
    "NUMERIC AMBIGUITY AUDIT"
)
print("=" * 112)


report = {
    "models": {}
}

grand = Counter()


for model in MODELS:

    p = (
        ROOT
        / f"{model}_correctness_final_v3.jsonl"
    )

    counts = Counter()
    by_dataset = Counter()
    by_condition = Counter()

    samples = []

    with p.open(
        "r",
        encoding="utf-8",
    ) as f:

        for line in f:

            if not line.strip():
                continue

            x = json.loads(line)

            if (
                x.get(
                    "correctness_method"
                )
                != "numeric_ambiguous"
            ):
                continue

            counts["total"] += 1

            dataset = x["dataset"]
            condition = x["condition"]

            by_dataset[
                dataset
            ] += 1

            by_condition[
                condition
            ] += 1

            answer = x.get(
                "answer_text"
            )

            explicit = (
                _explicit_numeric_answer_segment(
                    answer
                )
            )

            if explicit:
                counts[
                    "has_explicit_answer_cue"
                ] += 1
            else:
                counts[
                    "no_explicit_answer_cue"
                ] += 1

            mentions = (
                numeric_mentions(
                    answer
                )
            )

            counts[
                "numeric_mentions_total"
            ] += len(
                mentions
            )

            if len(samples) < 12:

                samples.append({
                    "instance_id":
                        x[
                            "instance_id"
                        ],

                    "dataset":
                        dataset,

                    "condition":
                        condition,

                    "gold_answer":
                        x.get(
                            "gold_answer"
                        ),

                    "answer_text":
                        answer,

                    "numeric_mentions":
                        mentions,

                    "explicit_answer_segment":
                        explicit,
                })


    report[
        "models"
    ][model] = {
        "counts":
            dict(counts),

        "by_dataset":
            dict(
                sorted(
                    by_dataset.items()
                )
            ),

        "by_condition":
            dict(
                sorted(
                    by_condition.items()
                )
            ),

        "samples":
            samples,
    }

    grand.update(
        counts
    )

    print(
        f"{model:16s} "
        f"ambiguous="
        f"{counts['total']:4d}  "
        f"explicit_cue="
        f"{counts['has_explicit_answer_cue']:4d}  "
        f"no_cue="
        f"{counts['no_explicit_answer_cue']:4d}  "
        f"FinQA="
        f"{by_dataset['finqa']:4d}  "
        f"TATQA="
        f"{by_dataset['tatqa']:4d}"
    )


report[
    "overall"
] = dict(
    grand
)

OUT.write_text(
    json.dumps(
        report,
        indent=2,
        ensure_ascii=False,
    ),
    encoding="utf-8",
)


print("-" * 112)

print(
    f"{'TOTAL':16s} "
    f"ambiguous="
    f"{grand['total']:5d}  "
    f"explicit_cue="
    f"{grand['has_explicit_answer_cue']:5d}  "
    f"no_cue="
    f"{grand['no_explicit_answer_cue']:5d}"
)

print("=" * 112)
print(
    "Audit:",
    OUT,
)

print(
    "PHASE 4C-3 NUMERIC AMBIGUITY AUDIT: COMPLETE"
)

print("=" * 112)
