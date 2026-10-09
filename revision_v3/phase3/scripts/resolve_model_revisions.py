import json
from pathlib import Path

from huggingface_hub import model_info


COHORT = Path(
    "revision_v3/phase3/contracts/"
    "model_cohort_v3.json"
)

OUT = Path(
    "revision_v3/phase3/contracts/"
    "model_revisions_v3.json"
)


cohort = json.loads(
    COHORT.read_text(
        encoding="utf-8"
    )
)

resolved = []

print("=" * 88)
print("DANGERMAP-RAG PHASE 3A: MODEL REVISION RESOLUTION")
print("=" * 88)

failed = []

for model in cohort["models"]:

    model_id = model["model_id"]

    print()
    print(model_id)

    try:
        info = model_info(
            model_id
        )

        sha = info.sha

        if not sha:
            raise RuntimeError(
                "No repository revision returned"
            )

        row = dict(model)
        row["revision"] = sha

        resolved.append(row)

        print(
            "  REVISION:",
            sha,
        )

        print(
            "  ACCESS: VERIFIED"
        )

    except Exception as exc:

        failed.append({
            "model_id":
                model_id,
            "error":
                repr(exc),
        })

        print(
            "  ACCESS: FAILED"
        )

        print(
            "  ERROR:",
            repr(exc),
        )


payload = {
    "version":
        "DangerMap-RAG-v3-model-revisions-1.0",

    "models":
        resolved,

    "failures":
        failed,
}


OUT.write_text(
    json.dumps(
        payload,
        indent=2,
    ),
    encoding="utf-8",
)

print()
print("=" * 88)

print(
    "Resolved:",
    len(resolved),
)

print(
    "Failed  :",
    len(failed),
)

print(
    "Manifest:",
    OUT,
)

if failed:
    print(
        "PHASE 3A MODEL ACCESS: INCOMPLETE"
    )
else:
    print(
        "PHASE 3A MODEL ACCESS: PASSED"
    )

print("=" * 88)
