import json
import re
from collections import Counter
from pathlib import Path


ROOT = Path(
    "revision_v3/phase3/outputs/pilot"
)

PILOT = Path(
    "revision_v3/phase3/pilot/"
    "pilot_instances_v3_12.jsonl"
)

OUT = Path(
    "revision_v3/phase3/results/"
    "pilot_canonical_parse_audit_v3.json"
)

MODELS = [
    "qwen25_3b",
    "qwen25_7b",
    "mistral_7b",
    "phi35_mini",
    "granite33_8b",
    "falcon3_7b",
]


def extract_json_objects(text):
    """
    Extract complete top-level {...} objects while respecting
    quoted strings and escapes.
    """
    objects = []

    depth = 0
    start = None
    in_string = False
    escaped = False

    for i, ch in enumerate(text):

        if in_string:
            if escaped:
                escaped = False
                continue

            if ch == "\\":
                escaped = True
                continue

            if ch == '"':
                in_string = False

            continue

        if ch == '"':
            in_string = True
            continue

        if ch == "{":
            if depth == 0:
                start = i

            depth += 1

        elif ch == "}":
            if depth == 0:
                continue

            depth -= 1

            if (
                depth == 0
                and start is not None
            ):
                candidate = text[
                    start:i + 1
                ]

                try:
                    obj = json.loads(
                        candidate
                    )

                    if isinstance(
                        obj,
                        dict,
                    ):
                        objects.append(
                            (
                                candidate,
                                obj,
                            )
                        )

                except json.JSONDecodeError:
                    pass

                start = None

    return objects


def canonicalize_citation(
    citation,
    valid_doc_ids,
):
    if not isinstance(
        citation,
        str,
    ):
        return (
            citation,
            False,
            False,
        )

    citation = citation.strip()

    if citation in valid_doc_ids:
        return (
            citation,
            False,
            True,
        )

    m = re.fullmatch(
        r"(?i)doc_id\s*:\s*(.+?)\s*",
        citation,
    )

    if m:
        candidate = (
            m.group(1).strip()
        )

        if candidate in valid_doc_ids:
            return (
                candidate,
                True,
                True,
            )

    return (
        citation,
        False,
        False,
    )


def canonicalize_object(
    obj,
    valid_doc_ids,
):
    out = dict(obj)

    normalized = 0
    invalid = []

    citations = out.get(
        "citations"
    )

    if isinstance(
        citations,
        list,
    ):
        fixed = []

        for citation in citations:
            (
                canonical,
                changed,
                valid,
            ) = canonicalize_citation(
                citation,
                valid_doc_ids,
            )

            fixed.append(
                canonical
            )

            if changed:
                normalized += 1

            if not valid:
                invalid.append(
                    canonical
                )

        out["citations"] = fixed

    return (
        out,
        normalized,
        invalid,
    )


def validate_schema(
    obj,
    valid_doc_ids,
):
    errors = []

    required = {
        "answer",
        "abstain",
        "expressed_confidence",
        "citations",
        "explanation",
    }

    missing = (
        required
        - set(obj)
    )

    if missing:
        errors.append(
            "missing_fields:"
            + ",".join(
                sorted(missing)
            )
        )

    if (
        "answer" in obj
        and not isinstance(
            obj["answer"],
            str,
        )
    ):
        errors.append(
            "answer_not_string"
        )

    if (
        "abstain" in obj
        and not isinstance(
            obj["abstain"],
            bool,
        )
    ):
        errors.append(
            "abstain_not_bool"
        )

    if "expressed_confidence" in obj:
        c = obj[
            "expressed_confidence"
        ]

        if (
            isinstance(c, bool)
            or not isinstance(
                c,
                (int, float),
            )
        ):
            errors.append(
                "confidence_not_number"
            )

        elif not (
            0 <= float(c) <= 100
        ):
            errors.append(
                "confidence_out_of_range"
            )

    if "citations" in obj:

        citations = obj[
            "citations"
        ]

        if not isinstance(
            citations,
            list,
        ):
            errors.append(
                "citations_not_list"
            )

        else:
            for citation in citations:

                if not isinstance(
                    citation,
                    str,
                ):
                    errors.append(
                        "citation_not_string"
                    )

                elif (
                    citation
                    not in valid_doc_ids
                ):
                    errors.append(
                        "invalid_citation:"
                        + citation
                    )

    if (
        "explanation" in obj
        and not isinstance(
            obj["explanation"],
            str,
        )
    ):
        errors.append(
            "explanation_not_string"
        )

    return errors


pilot_rows = [
    json.loads(x)
    for x in PILOT.read_text(
        encoding="utf-8"
    ).splitlines()
    if x.strip()
]

pilot_by_id = {
    x["instance_id"]: x
    for x in pilot_rows
}


report = {
    "models": {},
}

print("=" * 100)
print(
    "DANGERMAP-RAG PHASE 3B-2: "
    "CANONICAL PARSING AUDIT"
)
print("=" * 100)

grand = Counter()


for model in MODELS:

    fp = ROOT / (
        f"{model}_pilot_v3.jsonl"
    )

    rows = [
        json.loads(x)
        for x in fp.read_text(
            encoding="utf-8"
        ).splitlines()
        if x.strip()
    ]

    counts = Counter()
    cases = []

    for row in rows:

        instance = pilot_by_id[
            row["instance_id"]
        ]

        valid_doc_ids = {
            str(d["doc_id"])
            for d in
            instance[
                "evidence_docs"
            ]
        }

        raw = row[
            "raw_output"
        ]

        objects = (
            extract_json_objects(
                raw
            )
        )

        counts[
            "total"
        ] += 1

        if row[
            "strict_json_valid"
        ]:
            counts[
                "strict_valid"
            ] += 1

        if len(objects) > 1:
            counts[
                "multiple_objects"
            ] += 1

        if not objects:
            counts[
                "no_recoverable_object"
            ] += 1

            cases.append({
                "instance_id":
                    row[
                        "instance_id"
                    ],
                "recovery":
                    "FAILED",
                "json_object_count":
                    0,
            })

            continue

        # Frozen policy:
        # first complete JSON object only.
        first_raw, first_obj = (
            objects[0]
        )

        counts[
            "recoverable_json"
        ] += 1

        (
            canonical,
            normalized_count,
            invalid_citations,
        ) = canonicalize_object(
            first_obj,
            valid_doc_ids,
        )

        schema_errors = (
            validate_schema(
                canonical,
                valid_doc_ids,
            )
        )

        if normalized_count:
            counts[
                "citation_prefix_"
                "normalizations"
            ] += normalized_count

        if invalid_citations:
            counts[
                "outputs_with_"
                "invalid_citations"
            ] += 1

            counts[
                "invalid_citations"
            ] += len(
                invalid_citations
            )

        canonical_valid = (
            not schema_errors
        )

        if canonical_valid:
            counts[
                "canonical_valid"
            ] += 1

        cases.append({
            "instance_id":
                row[
                    "instance_id"
                ],

            "strict_valid":
                bool(
                    row[
                        "strict_json_valid"
                    ]
                ),

            "json_object_count":
                len(objects),

            "canonical_valid":
                canonical_valid,

            "citation_prefix_"
            "normalizations":
                normalized_count,

            "invalid_citations":
                invalid_citations,

            "canonical_schema_errors":
                schema_errors,

            "first_object":
                canonical,
        })

    report["models"][
        model
    ] = {
        "counts":
            dict(counts),
        "cases":
            cases,
    }

    grand.update(counts)

    print(
        f"{model:16s} "
        f"strict="
        f"{counts['strict_valid']:2d}/12  "
        f"recoverable="
        f"{counts['recoverable_json']:2d}/12  "
        f"canonical="
        f"{counts['canonical_valid']:2d}/12  "
        f"multi="
        f"{counts['multiple_objects']:2d}  "
        f"prefix_fix="
        f"{counts['citation_prefix_normalizations']:2d}  "
        f"invalid_cite_outputs="
        f"{counts['outputs_with_invalid_citations']:2d}"
    )


report[
    "overall_counts"
] = dict(grand)

OUT.parent.mkdir(
    parents=True,
    exist_ok=True,
)

OUT.write_text(
    json.dumps(
        report,
        indent=2,
        ensure_ascii=False,
    ),
    encoding="utf-8",
)

print("-" * 100)

print(
    f"{'TOTAL':16s} "
    f"strict="
    f"{grand['strict_valid']:2d}/72  "
    f"recoverable="
    f"{grand['recoverable_json']:2d}/72  "
    f"canonical="
    f"{grand['canonical_valid']:2d}/72"
)

print()
print(
    "Audit:",
    OUT,
)

print("=" * 100)

if (
    grand[
        "recoverable_json"
    ] == 72
):
    print(
        "JSON RECOVERY GATE: PASSED"
    )
else:
    print(
        "JSON RECOVERY GATE: "
        "NEEDS REVIEW"
    )

print("=" * 100)
