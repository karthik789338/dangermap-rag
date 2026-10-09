import importlib.util
import json
import traceback
from collections import Counter, defaultdict
from pathlib import Path

SCRIPT = Path(
    "revision_v3/phase1b/scripts/"
    "build_perturbations_v3.py"
)

BASE = Path(
    "revision_v3/data/"
    "base_items_v3_2k.jsonl"
)

OUT = Path(
    "revision_v3/phase1b/"
    "partial_constructability_audit.json"
)

spec = importlib.util.spec_from_file_location(
    "dmv3",
    SCRIPT,
)

m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

rows = [
    json.loads(line)
    for line in BASE.read_text(
        encoding="utf-8"
    ).splitlines()
    if line.strip()
]

passed = []
failed = []

stats = defaultdict(list)

print("=" * 88)
print("DANGERMAP-RAG PARTIAL-CONSTRUCTABILITY AUDIT")
print("=" * 88)
print("Base items:", len(rows))
print()

for idx, base in enumerate(rows, 1):

    try:
        gold = m.prepared_gold(
            base,
            3000,
        )

        partial, ratio = m.partial_docs(
            base,
            gold,
        )

        leaks = []

        for d in partial:
            if (
                m.answer_family(
                    base["gold_answer"]
                )
                not in {
                    "ynm",
                    "fever_label",
                }
                and m.answer_leak(
                    d["text"],
                    base["gold_answer"],
                )
            ):
                leaks.append(
                    d["doc_id"]
                )

        if leaks:
            raise RuntimeError(
                "direct_answer_leak="
                + repr(leaks)
            )

        if not (
            0.0 < ratio <= 0.80
        ):
            raise RuntimeError(
                f"invalid_ratio={ratio}"
            )

        stats[
            base["dataset"]
        ].append(ratio)

        passed.append({
            "base_id":
                base["base_id"],
            "dataset":
                base["dataset"],
            "ratio":
                ratio,
            "n_partial_docs":
                len(partial),
        })

    except Exception as exc:

        failed.append({
            "base_id":
                base["base_id"],
            "dataset":
                base["dataset"],
            "task_type":
                base["task_type"],
            "gold_answer":
                base["gold_answer"],
            "error":
                repr(exc),
            "question":
                base["question"],
            "gold_evidence": [
                {
                    "doc_id":
                        d.get(
                            "doc_id"
                        ),
                    "title":
                        d.get(
                            "title"
                        ),
                    "text":
                        str(
                            d.get(
                                "text",
                                ""
                            )
                        )[:2500],
                }
                for d in
                base.get(
                    "gold_evidence",
                    []
                )
            ],
        })

    if idx % 250 == 0:
        print(
            f"Processed {idx:4d}/"
            f"{len(rows)}"
        )

failure_counts = Counter(
    x["dataset"]
    for x in failed
)

summary = {
    "total":
        len(rows),

    "passed":
        len(passed),

    "failed":
        len(failed),

    "failure_counts":
        dict(
            sorted(
                failure_counts.items()
            )
        ),

    "ratio_by_dataset": {},
}

for ds, vals in sorted(
    stats.items()
):
    vals = sorted(vals)

    if not vals:
        continue

    n = len(vals)

    summary[
        "ratio_by_dataset"
    ][ds] = {
        "n": n,
        "min": vals[0],
        "median": (
            vals[n // 2]
            if n % 2
            else (
                vals[n // 2 - 1]
                + vals[n // 2]
            ) / 2
        ),
        "max": vals[-1],
        "mean":
            sum(vals) / n,
    }

OUT.write_text(
    json.dumps(
        {
            "summary":
                summary,
            "failures":
                failed,
        },
        indent=2,
    ),
    encoding="utf-8",
)

print()
print("=" * 88)
print("SUMMARY")
print("=" * 88)

print(
    json.dumps(
        summary,
        indent=2,
    )
)

print()
print("FIRST FAILURES:")

for x in failed[:30]:
    print(
        f"{x['dataset']:12s} "
        f"{x['base_id']:25s} "
        f"{x['error']}"
    )

print()
print("Audit file:", OUT)

print("=" * 88)

if failed:
    print(
        "PARTIAL CONSTRUCTABILITY: "
        "INCOMPLETE"
    )
else:
    print(
        "PARTIAL CONSTRUCTABILITY: "
        "PASSED"
    )

print("=" * 88)
