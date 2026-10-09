import json
import re
from collections import Counter
from pathlib import Path


BENCH = Path(
    "revision_v3/data/"
    "dangermap_instances_v3_1_12k.jsonl"
)

INPUT_ROOT = Path(
    "revision_v3/phase3/outputs/full"
)

OUTPUT_ROOT = Path(
    "revision_v3/phase3/canonical"
)

RESULT = Path(
    "revision_v3/phase3/results/final_audit/"
    "canonical_parse_summary_v3.json"
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
                            obj
                        )

                except json.JSONDecodeError:
                    pass

                start = None

    return objects


def normalize_citation(
    citation,
    valid_ids,
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

    citation = (
        citation.strip()
    )

    if citation in valid_ids:
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
            m.group(1)
            .strip()
        )

        if candidate in valid_ids:
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


def validate(
    obj,
    valid_ids,
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

    citations = obj.get(
        "citations"
    )

    if not isinstance(
        citations,
        list,
    ):
        errors.append(
            "citations_not_list"
        )

    else:
        for c in citations:

            if not isinstance(
                c,
                str,
            ):
                errors.append(
                    "citation_not_string"
                )

            elif c not in valid_ids:
                errors.append(
                    "invalid_citation:"
                    + c
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


benchmark = {}

with BENCH.open(
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


OUTPUT_ROOT.mkdir(
    parents=True,
    exist_ok=True,
)

summary = {
    "models": {},
}


print("=" * 112)
print(
    "DANGERMAP-RAG PHASE 3D-2: "
    "FULL CANONICAL OUTPUT PARSING"
)
print("=" * 112)


for model in MODELS:

    inp = (
        INPUT_ROOT
        / f"{model}_full_v3.jsonl"
    )

    out = (
        OUTPUT_ROOT
        / f"{model}_canonical_v3.jsonl"
    )

    counts = Counter()

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

            x = json.loads(line)

            iid = x[
                "instance_id"
            ]

            instance = benchmark[
                iid
            ]

            valid_ids = {
                str(d["doc_id"])
                for d in
                instance[
                    "evidence_docs"
                ]
            }

            objects = (
                extract_json_objects(
                    x["raw_output"]
                )
            )

            counts["total"] += 1

            if x.get(
                "strict_json_valid"
            ):
                counts[
                    "strict_valid"
                ] += 1

            if len(objects) > 1:
                counts[
                    "multiple_objects"
                ] += 1

            canonical = None
            normalization_count = 0
            invalid_citations = []
            schema_errors = []

            if objects:

                counts[
                    "recoverable"
                ] += 1

                canonical = dict(
                    objects[0]
                )

                citations = canonical.get(
                    "citations"
                )

                if isinstance(
                    citations,
                    list,
                ):

                    fixed = []

                    for citation in citations:

                        (
                            normalized,
                            changed,
                            valid,
                        ) = normalize_citation(
                            citation,
                            valid_ids,
                        )

                        fixed.append(
                            normalized
                        )

                        if changed:
                            normalization_count += 1

                        if not valid:
                            invalid_citations.append(
                                normalized
                            )

                    canonical[
                        "citations"
                    ] = fixed

                schema_errors = validate(
                    canonical,
                    valid_ids,
                )

                if normalization_count:
                    counts[
                        "citation_prefix_normalizations"
                    ] += normalization_count

                    counts[
                        "outputs_with_prefix_normalization"
                    ] += 1

                if invalid_citations:
                    counts[
                        "outputs_with_invalid_citations"
                    ] += 1

                    counts[
                        "invalid_citations"
                    ] += len(
                        invalid_citations
                    )

                if not schema_errors:
                    counts[
                        "canonical_valid"
                    ] += 1

            else:
                counts[
                    "unrecoverable"
                ] += 1

            if x.get(
                "hit_max_new_tokens"
            ):
                counts[
                    "hit_max_new_tokens"
                ] += 1

            row = {
                "model_short_name":
                    model,

                "instance_id":
                    iid,

                "base_id":
                    x["base_id"],

                "dataset":
                    x["dataset"],

                "condition":
                    x["condition"],

                "strict_json_valid":
                    bool(
                        x.get(
                            "strict_json_valid"
                        )
                    ),

                "json_object_count":
                    len(objects),

                "recoverable":
                    bool(objects),

                "canonical_output":
                    canonical,

                "canonical_valid":
                    (
                        bool(objects)
                        and not schema_errors
                    ),

                "citation_prefix_normalizations":
                    normalization_count,

                "invalid_citations":
                    invalid_citations,

                "canonical_schema_errors":
                    schema_errors,

                "hit_max_new_tokens":
                    bool(
                        x.get(
                            "hit_max_new_tokens"
                        )
                    ),

                "input_tokens":
                    x["input_tokens"],

                "output_tokens":
                    x["output_tokens"],
            }

            fout.write(
                json.dumps(
                    row,
                    ensure_ascii=False,
                )
                + "\n"
            )


    summary[
        "models"
    ][model] = dict(
        counts
    )


    print(
        f"{model:16s} "
        f"strict={counts['strict_valid']:5d}/12000  "
        f"recoverable={counts['recoverable']:5d}/12000  "
        f"canonical={counts['canonical_valid']:5d}/12000  "
        f"invalid_cite_outputs="
        f"{counts['outputs_with_invalid_citations']:4d}  "
        f"multi={counts['multiple_objects']:4d}  "
        f"cap={counts['hit_max_new_tokens']:3d}"
    )


RESULT.write_text(
    json.dumps(
        summary,
        indent=2,
    ),
    encoding="utf-8",
)


print("=" * 112)

recoverable_total = sum(
    x.get(
        "recoverable",
        0,
    )
    for x in summary[
        "models"
    ].values()
)

canonical_total = sum(
    x.get(
        "canonical_valid",
        0,
    )
    for x in summary[
        "models"
    ].values()
)

cap_total = sum(
    x.get(
        "hit_max_new_tokens",
        0,
    )
    for x in summary[
        "models"
    ].values()
)

print(
    "TOTAL RECOVERABLE :",
    f"{recoverable_total}/72000",
)

print(
    "TOTAL CANONICAL   :",
    f"{canonical_total}/72000",
)

print(
    "TOTAL CAP HITS    :",
    cap_total,
)

print("=" * 112)
print(
    "PHASE 3D-2 CANONICAL PARSING: COMPLETE"
)
print("=" * 112)
print(
    "Report:",
    RESULT,
)
