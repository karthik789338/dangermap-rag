import json
import sys
from collections import Counter
from pathlib import Path


sys.path.insert(
    0,
    "revision_v3/phase3/scripts",
)

from canonicalize_full_outputs_v3 import (
    extract_json_objects,
    normalize_citation,
    validate,
)


BENCH = Path(
    "revision_v3/data/"
    "dangermap_instances_v3_1_12k.jsonl"
)

ROOT = Path(
    "revision_v3/phase3/outputs/"
    "cap_extensions"
)

OUT = Path(
    "revision_v3/phase3/results/"
    "cap_extensions/"
    "cap_extension_final_audit_v3.json"
)


MODELS = [
    "qwen25_3b",
    "mistral_7b",
    "phi35_mini",
    "granite33_8b",
    "falcon3_7b",
]


EXPECTED = {
    "qwen25_3b": 2,
    "mistral_7b": 1,
    "phi35_mini": 53,
    "granite33_8b": 2,
    "falcon3_7b": 4,
}


benchmark = {}

with BENCH.open(
    "r",
    encoding="utf-8",
) as f:
    for line in f:
        if line.strip():
            x = json.loads(line)
            benchmark[
                x["instance_id"]
            ] = x


report = {
    "models": {}
}


print("=" * 105)
print(
    "DANGERMAP-RAG PHASE 3D-4: "
    "CAP EXTENSION FINAL AUDIT"
)
print("=" * 105)


grand = Counter()


for model in MODELS:

    path = (
        ROOT
        / f"{model}_cap_extensions_v3.jsonl"
    )

    rows = [
        json.loads(x)
        for x in path.read_text(
            encoding="utf-8"
        ).splitlines()
        if x.strip()
    ]

    counts = Counter()

    for row in rows:

        counts["rows"] += 1

        if row[
            "prefix_match_1024"
        ]:
            counts[
                "prefix_match"
            ] += 1

        if row[
            "hit_2048_cap"
        ]:
            counts[
                "hit_2048"
            ] += 1

        raw = row[
            "extended_raw_output"
        ]

        objects = (
            extract_json_objects(
                raw
            )
        )

        if not objects:
            counts[
                "unrecoverable"
            ] += 1
            continue

        counts[
            "recoverable"
        ] += 1

        obj = dict(
            objects[0]
        )

        instance = benchmark[
            row["instance_id"]
        ]

        valid_ids = {
            str(d["doc_id"])
            for d in instance[
                "evidence_docs"
            ]
        }

        citations = obj.get(
            "citations"
        )

        if isinstance(
            citations,
            list,
        ):
            fixed = []

            for c in citations:

                (
                    canonical,
                    changed,
                    valid,
                ) = normalize_citation(
                    c,
                    valid_ids,
                )

                fixed.append(
                    canonical
                )

                if changed:
                    counts[
                        "prefix_normalizations"
                    ] += 1

                if not valid:
                    counts[
                        "invalid_citations"
                    ] += 1

            obj["citations"] = fixed

        errors = validate(
            obj,
            valid_ids,
        )

        if not errors:
            counts[
                "canonical_valid"
            ] += 1

        else:
            counts[
                "canonical_invalid"
            ] += 1


    if (
        counts["rows"]
        != EXPECTED[model]
    ):
        raise RuntimeError(
            f"{model}: expected "
            f"{EXPECTED[model]} rows, "
            f"found {counts['rows']}"
        )

    report[
        "models"
    ][model] = dict(
        counts
    )

    grand.update(counts)

    print(
        f"{model:16s} "
        f"rows={counts['rows']:3d} "
        f"prefix={counts['prefix_match']:3d} "
        f"recoverable="
        f"{counts['recoverable']:3d} "
        f"canonical="
        f"{counts['canonical_valid']:3d} "
        f"invalid="
        f"{counts['canonical_invalid']:3d} "
        f"cap2048="
        f"{counts['hit_2048']:3d}"
    )


report[
    "overall"
] = dict(grand)

OUT.write_text(
    json.dumps(
        report,
        indent=2,
    ),
    encoding="utf-8",
)


print("-" * 105)
print(
    f"{'TOTAL':16s} "
    f"rows={grand['rows']:3d} "
    f"prefix={grand['prefix_match']:3d} "
    f"recoverable="
    f"{grand['recoverable']:3d} "
    f"canonical="
    f"{grand['canonical_valid']:3d} "
    f"invalid="
    f"{grand['canonical_invalid']:3d} "
    f"cap2048="
    f"{grand['hit_2048']:3d}"
)

print("=" * 105)

if (
    grand["rows"] != 62
    or grand["prefix_match"] != 62
):
    print(
        "CAP EXTENSION AUDIT: FAILED"
    )
    raise SystemExit(1)

print(
    "CAP EXTENSION REPRODUCIBILITY: PASSED"
)

print("=" * 105)
