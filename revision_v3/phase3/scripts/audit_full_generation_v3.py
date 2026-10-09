import hashlib
import json
from collections import Counter
from pathlib import Path


BENCH = Path(
    "revision_v3/data/"
    "dangermap_instances_v3_1_12k.jsonl"
)

OUT_ROOT = Path(
    "revision_v3/phase3/outputs/full"
)

RESULT = Path(
    "revision_v3/phase3/results/final_audit/"
    "full_generation_integrity_v3.json"
)

MODELS = [
    "qwen25_3b",
    "qwen25_7b",
    "mistral_7b",
    "phi35_mini",
    "granite33_8b",
    "falcon3_7b",
]


def sha256(path):
    h = hashlib.sha256()

    with path.open("rb") as f:
        for block in iter(
            lambda: f.read(1024 * 1024),
            b"",
        ):
            h.update(block)

    return h.hexdigest()


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
        ] = {
            "base_id":
                x["base_id"],

            "dataset":
                x["dataset"],

            "condition":
                x["condition"],
        }


assert len(benchmark) == 12000


report = {
    "benchmark_sha256":
        sha256(BENCH),

    "benchmark_rows":
        len(benchmark),

    "models": {},
}


global_fail = False
needs_review = False


print("=" * 108)
print(
    "DANGERMAP-RAG PHASE 3D-1: "
    "FULL 72K GENERATION INTEGRITY AUDIT"
)
print("=" * 108)


for model in MODELS:

    path = (
        OUT_ROOT
        / f"{model}_full_v3.jsonl"
    )

    if not path.exists():
        print(
            f"{model:16s} MISSING"
        )

        report[
            "models"
        ][model] = {
            "status": "MISSING"
        }

        global_fail = True
        continue

    seen = set()

    rows = 0
    duplicates = 0
    unknown_ids = 0
    metadata_mismatches = 0

    strict_valid = 0
    max_input = 0
    max_output = 0
    cap_hits = 0

    condition_counts = Counter()
    dataset_counts = Counter()
    contracts = Counter()

    eos_values = Counter()
    pad_values = Counter()

    with path.open(
        "r",
        encoding="utf-8",
    ) as f:

        for line_no, line in enumerate(
            f,
            1,
        ):
            if not line.strip():
                continue

            try:
                x = json.loads(line)

            except Exception as exc:
                raise RuntimeError(
                    f"{model}: corrupt JSONL "
                    f"line {line_no}: {exc}"
                )

            rows += 1

            iid = x[
                "instance_id"
            ]

            if iid in seen:
                duplicates += 1
            else:
                seen.add(iid)

            expected = benchmark.get(
                iid
            )

            if expected is None:
                unknown_ids += 1

            else:
                for key in [
                    "base_id",
                    "dataset",
                    "condition",
                ]:
                    if (
                        x.get(key)
                        != expected[key]
                    ):
                        metadata_mismatches += 1
                        break

            condition_counts[
                x["condition"]
            ] += 1

            dataset_counts[
                x["dataset"]
            ] += 1

            strict_valid += int(
                bool(
                    x.get(
                        "strict_json_valid"
                    )
                )
            )

            inp = int(
                x["input_tokens"]
            )

            out = int(
                x["output_tokens"]
            )

            max_input = max(
                max_input,
                inp,
            )

            max_output = max(
                max_output,
                out,
            )

            cap_hits += int(
                bool(
                    x.get(
                        "hit_max_new_tokens"
                    )
                )
            )

            contracts[
                str(
                    x.get(
                        "generation_contract"
                    )
                )
            ] += 1

            eos_values[
                str(
                    x.get(
                        "generation_eos_token_id"
                    )
                )
            ] += 1

            pad_values[
                str(
                    x.get(
                        "generation_pad_token_id"
                    )
                )
            ] += 1


    missing_ids = (
        set(benchmark)
        - seen
    )

    model_errors = []

    if rows != 12000:
        model_errors.append(
            f"rows={rows}"
        )

    if len(seen) != 12000:
        model_errors.append(
            f"unique_ids={len(seen)}"
        )

    if duplicates:
        model_errors.append(
            f"duplicates={duplicates}"
        )

    if unknown_ids:
        model_errors.append(
            f"unknown_ids={unknown_ids}"
        )

    if missing_ids:
        model_errors.append(
            f"missing_ids={len(missing_ids)}"
        )

    if metadata_mismatches:
        model_errors.append(
            "metadata_mismatches="
            f"{metadata_mismatches}"
        )

    if max_input > 12000:
        model_errors.append(
            f"max_input={max_input}"
        )

    expected_conditions = {
        "clean": 2000,
        "missing": 2000,
        "partial": 2000,
        "noisy": 2000,
        "contradictory": 2000,
        "stale": 2000,
    }

    if (
        dict(condition_counts)
        != expected_conditions
    ):
        model_errors.append(
            "condition_counts_invalid"
        )

    if cap_hits:
        needs_review = True

    status = (
        "FAIL"
        if model_errors
        else (
            "PASS_WITH_CAP_REVIEW"
            if cap_hits
            else "PASS"
        )
    )

    if model_errors:
        global_fail = True

    report[
        "models"
    ][model] = {
        "status":
            status,

        "rows":
            rows,

        "unique_instance_ids":
            len(seen),

        "duplicates":
            duplicates,

        "unknown_ids":
            unknown_ids,

        "missing_ids":
            len(missing_ids),

        "metadata_mismatches":
            metadata_mismatches,

        "strict_json_valid":
            strict_valid,

        "strict_json_valid_rate":
            strict_valid / rows,

        "max_input_tokens":
            max_input,

        "max_output_tokens":
            max_output,

        "hit_max_new_tokens":
            cap_hits,

        "condition_counts":
            dict(
                sorted(
                    condition_counts.items()
                )
            ),

        "dataset_counts":
            dict(
                sorted(
                    dataset_counts.items()
                )
            ),

        "generation_contracts":
            dict(contracts),

        "native_eos_values":
            dict(eos_values),

        "pad_values":
            dict(pad_values),

        "output_sha256":
            sha256(path),

        "errors":
            model_errors,
    }


    print(
        f"{model:16s} "
        f"rows={rows:5d} "
        f"unique={len(seen):5d} "
        f"strict={strict_valid:5d}/12000 "
        f"max_in={max_input:5d} "
        f"max_out={max_output:4d} "
        f"cap_hits={cap_hits:4d} "
        f"{status}"
    )


RESULT.write_text(
    json.dumps(
        report,
        indent=2,
    ),
    encoding="utf-8",
)


print("=" * 108)

if global_fail:
    print(
        "PHASE 3D-1 GENERATION INTEGRITY: FAILED"
    )
    raise SystemExit(1)

if needs_review:
    print(
        "PHASE 3D-1 GENERATION INTEGRITY: "
        "PASSED — OUTPUT CAP CASES REQUIRE REVIEW"
    )
else:
    print(
        "PHASE 3D-1 GENERATION INTEGRITY: PASSED"
    )

print("=" * 108)
print(
    "Report:",
    RESULT,
)
