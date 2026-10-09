import json
from collections import Counter
from pathlib import Path


FULL_ROOT = Path(
    "revision_v3/phase3/outputs/full"
)

CANON_ROOT = Path(
    "revision_v3/phase3/canonical"
)

RESULT_ROOT = Path(
    "revision_v3/phase3/results/final_audit"
)

RESULT_ROOT.mkdir(
    parents=True,
    exist_ok=True,
)

SUMMARY_PATH = (
    RESULT_ROOT
    / "cap_and_parse_failure_audit_v3.json"
)

CAP_REVIEW_PATH = (
    RESULT_ROOT
    / "cap_hits_needing_review_v3.jsonl"
)


MODELS = [
    "qwen25_3b",
    "qwen25_7b",
    "mistral_7b",
    "phi35_mini",
    "granite33_8b",
    "falcon3_7b",
]


def error_class(error):
    if error.startswith(
        "invalid_citation:"
    ):
        return "invalid_citation"

    if error.startswith(
        "missing_fields:"
    ):
        return "missing_fields"

    return error


report = {
    "models": {}
}

cap_review_rows = []


print("=" * 116)
print(
    "DANGERMAP-RAG PHASE 3D-3: "
    "CAP-HIT + CANONICAL FAILURE AUDIT"
)
print("=" * 116)


for model in MODELS:

    full_path = (
        FULL_ROOT
        / f"{model}_full_v3.jsonl"
    )

    canon_path = (
        CANON_ROOT
        / f"{model}_canonical_v3.jsonl"
    )

    full = {}

    with full_path.open(
        "r",
        encoding="utf-8",
    ) as f:

        for line in f:

            if not line.strip():
                continue

            x = json.loads(line)

            full[
                x["instance_id"]
            ] = x


    canonical = {}

    with canon_path.open(
        "r",
        encoding="utf-8",
    ) as f:

        for line in f:

            if not line.strip():
                continue

            x = json.loads(line)

            canonical[
                x["instance_id"]
            ] = x


    assert len(full) == 12000
    assert len(canonical) == 12000
    assert set(full) == set(canonical)


    all_failures = Counter()

    cap_counts = Counter()

    cap_by_dataset = Counter()
    cap_by_condition = Counter()

    cap_failure_classes = Counter()


    for iid, c in canonical.items():

        # ------------------------------------------------------
        # Overall canonical failure taxonomy
        # ------------------------------------------------------
        if not c["recoverable"]:

            all_failures[
                "unrecoverable_json"
            ] += 1

        elif not c[
            "canonical_valid"
        ]:

            errors = c.get(
                "canonical_schema_errors",
                [],
            )

            if not errors:

                all_failures[
                    "canonical_invalid_"
                    "without_recorded_error"
                ] += 1

            else:

                classes = {
                    error_class(e)
                    for e in errors
                }

                for cls in classes:

                    all_failures[
                        cls
                    ] += 1


        # ------------------------------------------------------
        # Output-cap cases
        # ------------------------------------------------------
        if not c[
            "hit_max_new_tokens"
        ]:
            continue

        cap_counts[
            "total"
        ] += 1

        cap_by_dataset[
            c["dataset"]
        ] += 1

        cap_by_condition[
            c["condition"]
        ] += 1


        if c["recoverable"]:

            cap_counts[
                "recoverable"
            ] += 1

        else:

            cap_counts[
                "unrecoverable"
            ] += 1


        if c["canonical_valid"]:

            cap_counts[
                "canonical_valid"
            ] += 1

        else:

            cap_counts[
                "canonical_invalid"
            ] += 1


        errors = c.get(
            "canonical_schema_errors",
            [],
        )

        classes = {
            error_class(e)
            for e in errors
        }

        if not c["recoverable"]:

            classes.add(
                "unrecoverable_json"
            )


        for cls in classes:

            cap_failure_classes[
                cls
            ] += 1


        # Cases where the cap may have prevented us from
        # obtaining a usable first complete output.
        technical_review = (
            not c["recoverable"]
        )

        # Schema-invalid cap cases also need inspection,
        # but extending generation should only be considered
        # if the problem plausibly comes from truncation.
        schema_review = (
            c["recoverable"]
            and not c[
                "canonical_valid"
            ]
        )


        if (
            technical_review
            or schema_review
        ):

            raw = full[iid][
                "raw_output"
            ]

            cap_review_rows.append({
                "model":
                    model,

                "instance_id":
                    iid,

                "base_id":
                    c["base_id"],

                "dataset":
                    c["dataset"],

                "condition":
                    c["condition"],

                "output_tokens":
                    c["output_tokens"],

                "recoverable":
                    c["recoverable"],

                "canonical_valid":
                    c[
                        "canonical_valid"
                    ],

                "canonical_schema_errors":
                    errors,

                "invalid_citations":
                    c.get(
                        "invalid_citations",
                        [],
                    ),

                "json_object_count":
                    c[
                        "json_object_count"
                    ],

                "raw_output_tail":
                    raw[-1500:],
            })


    report[
        "models"
    ][model] = {

        "overall_failure_taxonomy":
            dict(
                sorted(
                    all_failures.items()
                )
            ),

        "cap": {
            "counts":
                dict(cap_counts),

            "by_dataset":
                dict(
                    sorted(
                        cap_by_dataset.items()
                    )
                ),

            "by_condition":
                dict(
                    sorted(
                        cap_by_condition.items()
                    )
                ),

            "failure_classes":
                dict(
                    sorted(
                        cap_failure_classes.items()
                    )
                ),
        },
    }


    print(
        f"{model:16s} "
        f"cap={cap_counts['total']:4d}  "
        f"recoverable="
        f"{cap_counts['recoverable']:4d}  "
        f"unrecoverable="
        f"{cap_counts['unrecoverable']:4d}  "
        f"canonical="
        f"{cap_counts['canonical_valid']:4d}  "
        f"canon_fail="
        f"{cap_counts['canonical_invalid']:4d}"
    )


print()
print("=" * 116)
print("OVERALL CANONICAL FAILURE TAXONOMY")
print("=" * 116)


for model in MODELS:

    print()
    print(model)

    taxonomy = (
        report[
            "models"
        ][model][
            "overall_failure_taxonomy"
        ]
    )

    if not taxonomy:

        print("  none")

    else:

        for key, value in taxonomy.items():

            print(
                f"  {key:40s} "
                f"{value:5d}"
            )


print()
print("=" * 116)
print("CAP-HIT FAILURE TAXONOMY")
print("=" * 116)


for model in MODELS:

    print()
    print(model)

    failures = (
        report[
            "models"
        ][model][
            "cap"
        ][
            "failure_classes"
        ]
    )

    if not failures:

        print("  none")

    else:

        for key, value in failures.items():

            print(
                f"  {key:40s} "
                f"{value:5d}"
            )


SUMMARY_PATH.write_text(
    json.dumps(
        report,
        indent=2,
    ),
    encoding="utf-8",
)


with CAP_REVIEW_PATH.open(
    "w",
    encoding="utf-8",
) as f:

    for row in cap_review_rows:

        f.write(
            json.dumps(
                row,
                ensure_ascii=False,
            )
            + "\n"
        )


print()
print("=" * 116)

print(
    "CAP CASES NEEDING REVIEW:",
    len(cap_review_rows),
)

print(
    "Summary:",
    SUMMARY_PATH,
)

print(
    "Review packet:",
    CAP_REVIEW_PATH,
)

print("=" * 116)
print(
    "PHASE 3D-3 FAILURE AUDIT: COMPLETE"
)
print("=" * 116)
