import hashlib
import json
from collections import Counter
from pathlib import Path


SRC = Path(
    "revision_v3/data/"
    "dangermap_instances_v3_1_12k.jsonl"
)

OUT = Path(
    "revision_v3/phase3/pilot/"
    "pilot_instances_v3_12.jsonl"
)

MANIFEST = Path(
    "revision_v3/phase3/pilot/"
    "pilot_manifest_v3.json"
)


TARGETS = [
    ("hotpotqa", "clean"),
    ("hotpotqa", "missing"),

    ("fever", "partial"),
    ("fever", "contradictory"),

    ("pubmedqa", "noisy"),
    ("pubmedqa", "stale"),

    ("cuad", "clean"),
    ("cuad", "partial"),

    ("casehold", "contradictory"),
    ("casehold", "stale"),

    ("finqa", "noisy"),
    ("tatqa", "missing"),
]


def stable_key(row):
    raw = (
        row["base_id"]
        + "::"
        + row["condition"]
        + "::phase3pilot"
    ).encode("utf-8")

    return hashlib.sha256(
        raw
    ).hexdigest()


rows = [
    json.loads(line)
    for line in SRC.read_text(
        encoding="utf-8"
    ).splitlines()
    if line.strip()
]

selected = []

for dataset, condition in TARGETS:

    candidates = [
        x for x in rows
        if (
            x["dataset"] == dataset
            and x["condition"] == condition
        )
    ]

    if not candidates:
        raise RuntimeError(
            f"No candidate for "
            f"{dataset}/{condition}"
        )

    candidates.sort(
        key=stable_key
    )

    selected.append(
        candidates[0]
    )


assert len(selected) == 12
assert len({
    x["instance_id"]
    for x in selected
}) == 12


condition_counts = Counter(
    x["condition"]
    for x in selected
)

expected_conditions = {
    "clean",
    "missing",
    "partial",
    "noisy",
    "contradictory",
    "stale",
}

assert set(
    condition_counts
) == expected_conditions

assert all(
    condition_counts[x] == 2
    for x in expected_conditions
)


with OUT.open(
    "w",
    encoding="utf-8",
) as f:

    for row in selected:
        f.write(
            json.dumps(
                row,
                ensure_ascii=False,
            )
            + "\n"
        )


payload = {
    "pilot_size": 12,

    "selection":
        "deterministic SHA256-ranked "
        "selection within frozen "
        "dataset-condition targets",

    "targets": [
        {
            "dataset": d,
            "condition": c,
        }
        for d, c in TARGETS
    ],

    "instance_ids": [
        x["instance_id"]
        for x in selected
    ],

    "condition_counts":
        dict(
            sorted(
                condition_counts.items()
            )
        ),
}


MANIFEST.write_text(
    json.dumps(
        payload,
        indent=2,
    ),
    encoding="utf-8",
)


print("=" * 80)
print("DANGERMAP-RAG PHASE 3B-0: PILOT SET")
print("=" * 80)

for row in selected:
    print(
        f"{row['dataset']:12s} "
        f"{row['condition']:14s} "
        f"{row['instance_id']}"
    )

print()
print(
    "Condition counts:",
    dict(
        sorted(
            condition_counts.items()
        )
    ),
)

print("=" * 80)
print("PHASE 3B-0 PILOT SET: PASSED")
print("=" * 80)
