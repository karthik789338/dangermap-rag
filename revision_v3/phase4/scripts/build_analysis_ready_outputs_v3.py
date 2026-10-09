import json
import math
from collections import Counter
from pathlib import Path


BENCHMARK = Path(
    "revision_v3/data/"
    "dangermap_instances_v3_1_12k.jsonl"
)

CANON_ROOT = Path(
    "revision_v3/phase3/canonical"
)

OUT_ROOT = Path(
    "revision_v3/phase4/data"
)

SUMMARY_PATH = Path(
    "revision_v3/phase4/results/"
    "analysis_ready_summary_v3.json"
)


MODELS = [
    "qwen25_3b",
    "qwen25_7b",
    "mistral_7b",
    "phi35_mini",
    "granite33_8b",
    "falcon3_7b",
]


def normalize_answer(value):

    if isinstance(value, str):
        return (
            value.strip(),
            False,
            True,
        )

    if isinstance(value, bool):
        return (
            "true" if value else "false",
            True,
            True,
        )

    if isinstance(value, int):
        return (
            str(value),
            True,
            True,
        )

    if isinstance(value, float):

        if not math.isfinite(value):
            return (
                None,
                False,
                False,
            )

        return (
            str(value),
            True,
            True,
        )

    return (
        None,
        False,
        False,
    )


def normalize_confidence(value):

    if isinstance(value, bool):
        return None

    if not isinstance(
        value,
        (int, float),
    ):
        return None

    value = float(value)

    if not math.isfinite(value):
        return None

    if not (
        0.0 <= value <= 100.0
    ):
        return None

    return value / 100.0


benchmark = {}

with BENCHMARK.open(
    "r",
    encoding="utf-8",
) as f:

    for line in f:

        if not line.strip():
            continue

        x = json.loads(line)

        benchmark[
            x["instance_id"]
        ] = x


if len(benchmark) != 12000:
    raise RuntimeError(
        f"Expected 12000 benchmark rows; "
        f"found {len(benchmark)}"
    )


OUT_ROOT.mkdir(
    parents=True,
    exist_ok=True,
)

summary = {
    "models": {},
}


print("=" * 114)
print(
    "DANGERMAP-RAG PHASE 4A: "
    "ANALYSIS-READY RESPONSE EXTRACTION"
)
print("=" * 114)


for model in MODELS:

    inp = (
        CANON_ROOT
        / f"{model}_canonical_v3.jsonl"
    )

    out = (
        OUT_ROOT
        / f"{model}_analysis_ready_v3.jsonl"
    )

    counts = Counter()

    by_dataset = {}

    seen = set()

    with inp.open(
        "r",
        encoding="utf-8",
    ) as fin, out.open(
        "w",
        encoding="utf-8",
    ) as fout:

        for line in fin:

            if not line.strip():
                continue

            c = json.loads(line)

            iid = c[
                "instance_id"
            ]

            if iid in seen:
                raise RuntimeError(
                    f"{model}: duplicate {iid}"
                )

            seen.add(iid)

            instance = benchmark[
                iid
            ]

            obj = c.get(
                "canonical_output"
            )

            recoverable = (
                isinstance(
                    obj,
                    dict,
                )
            )

            counts["total"] += 1

            if recoverable:
                counts[
                    "recoverable"
                ] += 1

            # ----------------------------------------------
            # Answer
            # ----------------------------------------------
            answer_text = None
            answer_coerced = False
            answer_usable = False

            if recoverable:

                (
                    answer_text,
                    answer_coerced,
                    answer_usable,
                ) = normalize_answer(
                    obj.get(
                        "answer"
                    )
                )

            if answer_usable:
                counts[
                    "answer_usable"
                ] += 1

            if answer_coerced:
                counts[
                    "answer_scalar_coerced"
                ] += 1

            # ----------------------------------------------
            # Abstention
            # ----------------------------------------------
            abstained = None

            if (
                recoverable
                and isinstance(
                    obj.get("abstain"),
                    bool,
                )
            ):
                abstained = obj[
                    "abstain"
                ]

                counts[
                    "abstain_usable"
                ] += 1

            # ----------------------------------------------
            # Expressed confidence
            # ----------------------------------------------
            confidence = None

            if recoverable:
                confidence = (
                    normalize_confidence(
                        obj.get(
                            "expressed_confidence"
                        )
                    )
                )

            if confidence is not None:
                counts[
                    "confidence_usable"
                ] += 1

            # ----------------------------------------------
            # Citations
            # ----------------------------------------------
            citations = None
            citation_list_usable = False

            if (
                recoverable
                and isinstance(
                    obj.get("citations"),
                    list,
                )
            ):

                if all(
                    isinstance(x, str)
                    for x in
                    obj["citations"]
                ):
                    citations = [
                        x.strip()
                        for x in
                        obj["citations"]
                    ]

                    citation_list_usable = True

                    counts[
                        "citation_list_usable"
                    ] += 1

            valid_doc_ids = {
                str(d["doc_id"])
                for d in
                instance[
                    "evidence_docs"
                ]
            }

            valid_citations = []
            invalid_citations = []

            if citation_list_usable:

                for citation in citations:

                    if citation in valid_doc_ids:
                        valid_citations.append(
                            citation
                        )

                    else:
                        invalid_citations.append(
                            citation
                        )

                if invalid_citations:
                    counts[
                        "outputs_with_invalid_citations"
                    ] += 1

            # ----------------------------------------------
            # Explanation
            # ----------------------------------------------
            explanation = None

            if (
                recoverable
                and isinstance(
                    obj.get(
                        "explanation"
                    ),
                    str,
                )
            ):
                explanation = (
                    obj[
                        "explanation"
                    ].strip()
                )

                counts[
                    "explanation_usable"
                ] += 1

            # ----------------------------------------------
            # Metric availability
            # ----------------------------------------------
            semantic_answer_available = (
                answer_usable
            )

            sf_core_available = (
                answer_usable
                and abstained is not None
                and confidence is not None
                and citation_list_usable
            )

            if semantic_answer_available:
                counts[
                    "semantic_answer_available"
                ] += 1

            if sf_core_available:
                counts[
                    "sf_core_fields_available"
                ] += 1

            if c.get(
                "strict_json_valid"
            ):
                counts[
                    "strict_json_valid"
                ] += 1

            if c.get(
                "canonical_valid"
            ):
                counts[
                    "canonical_valid"
                ] += 1

            if c.get(
                "hit_max_new_tokens"
            ):
                counts[
                    "hit_max_new_tokens"
                ] += 1

            dataset = instance[
                "dataset"
            ]

            if dataset not in by_dataset:
                by_dataset[
                    dataset
                ] = Counter()

            by_dataset[
                dataset
            ]["total"] += 1

            if semantic_answer_available:
                by_dataset[
                    dataset
                ][
                    "semantic_answer_available"
                ] += 1

            if sf_core_available:
                by_dataset[
                    dataset
                ][
                    "sf_core_fields_available"
                ] += 1

            # ----------------------------------------------
            # Preserve benchmark + model fields
            # ----------------------------------------------
            row = {
                "model":
                    model,

                "instance_id":
                    iid,

                "base_id":
                    instance[
                        "base_id"
                    ],

                "dataset":
                    dataset,

                "domain":
                    instance.get(
                        "domain"
                    ),

                "task_type":
                    instance.get(
                        "task_type"
                    ),

                "condition":
                    instance[
                        "condition"
                    ],

                "question":
                    instance[
                        "question"
                    ],

                "gold_answer":
                    instance[
                        "gold_answer"
                    ],

                "should_abstain":
                    instance.get(
                        "should_abstain"
                    ),

                "evidence_docs":
                    instance[
                        "evidence_docs"
                    ],

                "strict_json_valid":
                    bool(
                        c.get(
                            "strict_json_valid"
                        )
                    ),

                "recoverable":
                    recoverable,

                "canonical_valid":
                    bool(
                        c.get(
                            "canonical_valid"
                        )
                    ),

                "hit_max_new_tokens":
                    bool(
                        c.get(
                            "hit_max_new_tokens"
                        )
                    ),

                "answer_text":
                    answer_text,

                "answer_scalar_coerced":
                    answer_coerced,

                "answer_usable":
                    answer_usable,

                "abstained":
                    abstained,

                "expressed_confidence":
                    confidence,

                "citations":
                    citations,

                "valid_citations":
                    valid_citations,

                "invalid_citations":
                    invalid_citations,

                "citation_list_usable":
                    citation_list_usable,

                "explanation":
                    explanation,

                "semantic_answer_available":
                    semantic_answer_available,

                "sf_core_fields_available":
                    sf_core_available,

                "canonical_schema_errors":
                    c.get(
                        "canonical_schema_errors",
                        [],
                    ),
            }

            fout.write(
                json.dumps(
                    row,
                    ensure_ascii=False,
                )
                + "\n"
            )


    if len(seen) != 12000:
        raise RuntimeError(
            f"{model}: expected 12000 "
            f"unique outputs, found "
            f"{len(seen)}"
        )


    summary[
        "models"
    ][model] = {

        "counts":
            dict(counts),

        "by_dataset": {
            dataset:
                dict(values)
            for dataset, values
            in sorted(
                by_dataset.items()
            )
        },
    }


    print(
        f"{model:16s} "
        f"recoverable="
        f"{counts['recoverable']:5d} "
        f"answer="
        f"{counts['answer_usable']:5d} "
        f"coerced="
        f"{counts['answer_scalar_coerced']:5d} "
        f"abstain="
        f"{counts['abstain_usable']:5d} "
        f"confidence="
        f"{counts['confidence_usable']:5d} "
        f"citations="
        f"{counts['citation_list_usable']:5d} "
        f"SF-core="
        f"{counts['sf_core_fields_available']:5d}"
    )


SUMMARY_PATH.write_text(
    json.dumps(
        summary,
        indent=2,
    ),
    encoding="utf-8",
)


print("=" * 114)

print(
    "Summary:",
    SUMMARY_PATH,
)

print(
    "PHASE 4A ANALYSIS-READY EXTRACTION: PASSED"
)

print("=" * 114)
