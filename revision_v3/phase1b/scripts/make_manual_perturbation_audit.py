import csv
import json
import re
from pathlib import Path


SRC = Path(
    "revision_v3/phase1b/"
    "perturbation_v3_manual_samples.jsonl"
)

OUT_MD = Path(
    "revision_v3/phase1b/"
    "manual_perturbation_audit_packet.md"
)

OUT_CSV = Path(
    "revision_v3/phase1b/"
    "manual_perturbation_audit_labels.csv"
)


def norm(x):
    return re.sub(
        r"\s+",
        " ",
        str(x or "")
    ).strip()


def short(x, n=1200):
    x = norm(x)

    if len(x) <= n:
        return x

    return x[:n] + " ..."


rows = [
    json.loads(line)
    for line in SRC.read_text(
        encoding="utf-8"
    ).splitlines()
    if line.strip()
]

rows = sorted(
    rows,
    key=lambda x: (
        x["dataset"],
        x["condition"],
    ),
)

if len(rows) != 42:
    raise RuntimeError(
        f"Expected 42 samples, got {len(rows)}"
    )


with OUT_MD.open(
    "w",
    encoding="utf-8",
) as f:

    f.write(
        "# DangerMap-RAG V3 Manual "
        "Perturbation Audit\n\n"
    )

    f.write(
        "Review criterion:\n\n"
        "- **clean**: sufficient support is present; no artificial distractor.\n"
        "- **missing**: decisive support is absent.\n"
        "- **partial**: topical/original support remains, but decisive support is removed.\n"
        "- **noisy**: sufficient gold support remains despite irrelevant semantic distractors.\n"
        "- **contradictory**: genuine-looking evidence supports incompatible answers without an explicit conflict cue.\n"
        "- **stale**: only an older answer-bearing snapshot is available, without explicit 'stale/outdated' wording.\n\n"
    )

    for i, x in enumerate(rows, 1):

        f.write(
            f"## Case {i:02d}: "
            f"{x['dataset']} / "
            f"{x['condition']}\n\n"
        )

        f.write(
            f"**Instance ID:** "
            f"`{x['instance_id']}`\n\n"
        )

        f.write(
            f"**Question:** "
            f"{norm(x['question'])}\n\n"
        )

        f.write(
            f"**Gold answer:** "
            f"{norm(x['gold_answer'])}\n\n"
        )

        f.write(
            f"**Expected abstention:** "
            f"{x['should_abstain']}\n\n"
        )

        if (
            x["condition"]
            == "partial"
        ):
            ratio = (
                x.get("metadata", {})
                .get(
                    "partial_retained_ratio"
                )
            )

            f.write(
                f"**Retained ratio:** "
                f"{ratio}\n\n"
            )

        f.write("**Evidence:**\n\n")

        for j, d in enumerate(
            x["evidence_docs"],
            1,
        ):
            f.write(
                f"### Document {j}\n\n"
            )

            f.write(
                f"- ID: `{d['doc_id']}`\n"
            )

            f.write(
                f"- Role: "
                f"`{d['evidence_role']}`\n"
            )

            f.write(
                f"- Source: "
                f"`{d['source']}`\n"
            )

            f.write(
                f"- Title: "
                f"{norm(d['title'])}\n\n"
            )

            f.write(
                short(d["text"])
                + "\n\n"
            )

        f.write(
            "**Human judgment:** "
            "PASS / FAIL / UNCERTAIN\n\n"
        )

        f.write(
            "**Reason:**\n\n---\n\n"
        )


columns = [
    "case_no",
    "instance_id",
    "dataset",
    "condition",
    "partial_retained_ratio",
    "condition_valid",
    "topical_relevance_present",
    "decisive_support_removed",
    "no_explicit_condition_cue",
    "evidence_sufficient_if_expected",
    "notes",
]

with OUT_CSV.open(
    "w",
    encoding="utf-8",
    newline="",
) as f:

    writer = csv.DictWriter(
        f,
        fieldnames=columns,
    )

    writer.writeheader()

    for i, x in enumerate(
        rows,
        1,
    ):
        writer.writerow({
            "case_no": i,
            "instance_id":
                x["instance_id"],
            "dataset":
                x["dataset"],
            "condition":
                x["condition"],
            "partial_retained_ratio":
                x.get(
                    "metadata",
                    {}
                ).get(
                    "partial_retained_ratio",
                    ""
                ),
            "condition_valid": "",
            "topical_relevance_present": "",
            "decisive_support_removed": "",
            "no_explicit_condition_cue": "",
            "evidence_sufficient_if_expected": "",
            "notes": "",
        })


print("=" * 76)
print(
    "DANGERMAP-RAG MANUAL "
    "PERTURBATION AUDIT PACKET"
)
print("=" * 76)

print("Samples:", len(rows))
print("Markdown:", OUT_MD)
print("Labels  :", OUT_CSV)

print()
print("Counts:")

from collections import Counter

for key, n in sorted(
    Counter(
        (
            x["dataset"],
            x["condition"],
        )
        for x in rows
    ).items()
):
    print(
        f"  {key[0]:12s} "
        f"{key[1]:14s}: {n}"
    )

print("=" * 76)
print("AUDIT PACKET CREATION: PASSED")
print("=" * 76)
