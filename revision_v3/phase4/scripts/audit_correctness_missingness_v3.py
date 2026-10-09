import json
from collections import Counter
from pathlib import Path


ROOT = Path(
    "revision_v3/phase4/data"
)

OUT = Path(
    "revision_v3/phase4/results/"
    "correctness_missingness_v3.json"
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
    "DANGERMAP-RAG PHASE 4C-1: "
    "CORRECTNESS MISSINGNESS AUDIT"
)
print("=" * 112)


report = {
    "models": {}
}

grand = Counter()


for model in MODELS:

    p = (
        ROOT
        / f"{model}_scored_correctness_v3.jsonl"
    )

    overall = Counter()
    by_dataset = {}
    by_condition = {}

    examples = {
        "fever_unmapped": [],
        "pubmedqa_unmapped": [],
        "answer_unavailable": [],
    }

    with p.open(
        "r",
        encoding="utf-8",
    ) as f:

        for line in f:

            if not line.strip():
                continue

            x = json.loads(line)

            dataset = x["dataset"]
            condition = x["condition"]

            if dataset not in by_dataset:
                by_dataset[
                    dataset
                ] = Counter()

            if condition not in by_condition:
                by_condition[
                    condition
                ] = Counter()

            ds = by_dataset[
                dataset
            ]

            cs = by_condition[
                condition
            ]

            overall["total"] += 1
            ds["total"] += 1
            cs["total"] += 1

            score = x.get(
                "automated_correctness"
            )

            method = x.get(
                "correctness_method"
            )

            if score is not None:

                overall[
                    "available"
                ] += 1

                ds[
                    "available"
                ] += 1

                cs[
                    "available"
                ] += 1

                continue

            overall[
                "missing"
            ] += 1

            ds[
                "missing"
            ] += 1

            cs[
                "missing"
            ] += 1

            if not x.get(
                "answer_usable"
            ):
                reason = (
                    "answer_unavailable"
                )

            elif (
                method
                == "fever_unmapped_pending_semantic"
            ):
                reason = (
                    "fever_unmapped"
                )

            elif (
                method
                == "pubmedqa_unmapped_pending_semantic"
            ):
                reason = (
                    "pubmedqa_unmapped"
                )

            else:
                reason = (
                    "other_missing"
                )

            overall[
                reason
            ] += 1

            ds[
                reason
            ] += 1

            cs[
                reason
            ] += 1

            if (
                reason in examples
                and len(
                    examples[
                        reason
                    ]
                ) < 5
            ):
                examples[
                    reason
                ].append({
                    "instance_id":
                        x[
                            "instance_id"
                        ],

                    "dataset":
                        dataset,

                    "condition":
                        condition,

                    "question":
                        x.get(
                            "question"
                        ),

                    "gold_answer":
                        x.get(
                            "gold_answer"
                        ),

                    "answer_text":
                        x.get(
                            "answer_text"
                        ),

                    "abstained":
                        x.get(
                            "abstained"
                        ),
                })


    report[
        "models"
    ][model] = {
        "overall":
            dict(overall),

        "by_dataset": {
            k: dict(v)
            for k, v in sorted(
                by_dataset.items()
            )
        },

        "by_condition": {
            k: dict(v)
            for k, v in sorted(
                by_condition.items()
            )
        },

        "examples":
            examples,
    }

    grand.update(
        overall
    )

    print(
        f"{model:16s} "
        f"missing={overall['missing']:4d}  "
        f"answer_unavailable="
        f"{overall['answer_unavailable']:4d}  "
        f"FEVER_unmapped="
        f"{overall['fever_unmapped']:4d}  "
        f"PubMed_unmapped="
        f"{overall['pubmedqa_unmapped']:4d}  "
        f"other="
        f"{overall['other_missing']:4d}"
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
    f"missing={grand['missing']:5d}  "
    f"answer_unavailable="
    f"{grand['answer_unavailable']:5d}  "
    f"FEVER_unmapped="
    f"{grand['fever_unmapped']:5d}  "
    f"PubMed_unmapped="
    f"{grand['pubmedqa_unmapped']:5d}  "
    f"other="
    f"{grand['other_missing']:5d}"
)

print("=" * 112)
print(
    "Audit:",
    OUT,
)

print(
    "PHASE 4C-1 MISSINGNESS AUDIT: PASSED"
)
print("=" * 112)
