import hashlib
import json
from collections import Counter
from pathlib import Path

import numpy as np
from transformers import AutoTokenizer


BENCHMARK = Path(
    "revision_v3/data/"
    "dangermap_instances_v3_1_12k.jsonl"
)

SYSTEM_PATH = Path(
    "revision_v3/phase3/contracts/"
    "system_prompt_v3.txt"
)

USER_TEMPLATE_PATH = Path(
    "revision_v3/phase3/contracts/"
    "user_prompt_template_v3.txt"
)

MODEL_MANIFEST = Path(
    "revision_v3/phase3/contracts/"
    "model_revisions_v3.json"
)

OUT_DIR = Path(
    "revision_v3/phase3/results/"
    "token_preflight_v3"
)

MAX_ALLOWED = 12000


def sha256(path):
    h = hashlib.sha256()

    with path.open("rb") as f:
        for chunk in iter(
            lambda: f.read(1024 * 1024),
            b"",
        ):
            h.update(chunk)

    return h.hexdigest()


def serialize_evidence(instance):
    parts = []

    for i, doc in enumerate(
        instance["evidence_docs"],
        1,
    ):
        parts.append(
            "\n".join([
                f"[Document {i}]",
                f"doc_id: {doc['doc_id']}",
                f"title: {doc.get('title', '')}",
                f"source: {doc.get('source', '')}",
                "text:",
                str(doc.get("text", "")),
            ])
        )

    return "\n\n".join(parts)


def build_messages(
    instance,
    system_prompt,
    user_template,
):
    evidence = serialize_evidence(
        instance
    )

    user = user_template.format(
        question=instance["question"],
        evidence=evidence,
    )

    return [
        {
            "role": "system",
            "content": system_prompt,
        },
        {
            "role": "user",
            "content": user,
        },
    ]


rows = [
    json.loads(line)
    for line in BENCHMARK.read_text(
        encoding="utf-8"
    ).splitlines()
    if line.strip()
]

models = json.loads(
    MODEL_MANIFEST.read_text(
        encoding="utf-8"
    )
)["models"]

system_prompt = SYSTEM_PATH.read_text(
    encoding="utf-8"
).strip()

user_template = USER_TEMPLATE_PATH.read_text(
    encoding="utf-8"
)

OUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

print("=" * 100)
print(
    "DANGERMAP-RAG PHASE 3B-4: "
    "FULL TOKENIZER PREFLIGHT"
)
print("=" * 100)

print(
    "Benchmark rows:",
    len(rows),
)

print(
    "Benchmark SHA:",
    sha256(BENCHMARK),
)

print(
    "Input ceiling:",
    MAX_ALLOWED,
)

assert len(rows) == 12000

global_fail = False
all_summaries = []


for model_cfg in models:

    short = model_cfg[
        "short_name"
    ]

    model_id = model_cfg[
        "model_id"
    ]

    revision = model_cfg[
        "revision"
    ]

    print()
    print("=" * 100)
    print(
        f"MODEL: {short}"
    )
    print(model_id)
    print(revision)
    print("=" * 100)

    tokenizer = (
        AutoTokenizer
        .from_pretrained(
            model_id,
            revision=revision,
            trust_remote_code=False,
        )
    )

    lengths = []
    details = []

    over_limit = []
    by_dataset = {}
    by_condition = {}

    for idx, instance in enumerate(
        rows,
        1,
    ):

        messages = build_messages(
            instance,
            system_prompt,
            user_template,
        )

        prompt_text = (
            tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True,
            )
        )

        encoded = tokenizer(
            prompt_text,
            add_special_tokens=False,
            truncation=False,
        )

        n_tokens = len(
            encoded["input_ids"]
        )

        lengths.append(
            n_tokens
        )

        details.append({
            "instance_id":
                instance["instance_id"],

            "base_id":
                instance["base_id"],

            "dataset":
                instance["dataset"],

            "condition":
                instance["condition"],

            "input_tokens":
                n_tokens,
        })

        by_dataset.setdefault(
            instance["dataset"],
            [],
        ).append(
            n_tokens
        )

        by_condition.setdefault(
            instance["condition"],
            [],
        ).append(
            n_tokens
        )

        if n_tokens > MAX_ALLOWED:
            over_limit.append(
                details[-1]
            )

        if idx % 1000 == 0:
            print(
                f"Processed "
                f"{idx:5d}/12000"
            )

    arr = np.asarray(
        lengths,
        dtype=int,
    )

    longest = sorted(
        details,
        key=lambda x:
            x["input_tokens"],
        reverse=True,
    )[:20]

    summary = {
        "model_short_name":
            short,

        "model_id":
            model_id,

        "revision":
            revision,

        "tokenizer_model_max_length":
            tokenizer.model_max_length,

        "rows":
            len(lengths),

        "min_tokens":
            int(arr.min()),

        "median_tokens":
            float(
                np.median(arr)
            ),

        "p90_tokens":
            float(
                np.quantile(
                    arr,
                    0.90,
                )
            ),

        "p95_tokens":
            float(
                np.quantile(
                    arr,
                    0.95,
                )
            ),

        "p99_tokens":
            float(
                np.quantile(
                    arr,
                    0.99,
                )
            ),

        "max_tokens":
            int(arr.max()),

        "count_gt_8000":
            int(
                (arr > 8000).sum()
            ),

        "count_gt_10000":
            int(
                (arr > 10000).sum()
            ),

        "count_gt_12000":
            int(
                (arr > 12000).sum()
            ),

        "dataset_maxima": {
            dataset:
                int(max(vals))
            for dataset, vals
            in sorted(
                by_dataset.items()
            )
        },

        "condition_maxima": {
            condition:
                int(max(vals))
            for condition, vals
            in sorted(
                by_condition.items()
            )
        },

        "top_20_longest":
            longest,
    }

    all_summaries.append(
        summary
    )

    (
        OUT_DIR
        / f"{short}_token_summary_v3.json"
    ).write_text(
        json.dumps(
            summary,
            indent=2,
        ),
        encoding="utf-8",
    )

    (
        OUT_DIR
        / f"{short}_all_lengths_v3.jsonl"
    ).write_text(
        "".join(
            json.dumps(
                x,
                ensure_ascii=False,
            )
            + "\n"
            for x in details
        ),
        encoding="utf-8",
    )

    if over_limit:
        (
            OUT_DIR
            / f"{short}_over_limit_v3.jsonl"
        ).write_text(
            "".join(
                json.dumps(
                    x,
                    ensure_ascii=False,
                )
                + "\n"
                for x in over_limit
            ),
            encoding="utf-8",
        )

    print()
    print(
        "min    :",
        summary["min_tokens"],
    )

    print(
        "median :",
        summary["median_tokens"],
    )

    print(
        "p95    :",
        summary["p95_tokens"],
    )

    print(
        "p99    :",
        summary["p99_tokens"],
    )

    print(
        "max    :",
        summary["max_tokens"],
    )

    print(
        ">8000  :",
        summary["count_gt_8000"],
    )

    print(
        ">10000 :",
        summary["count_gt_10000"],
    )

    print(
        ">12000 :",
        summary["count_gt_12000"],
    )

    if over_limit:
        print(
            "TOKEN PREFLIGHT: FAIL"
        )

        global_fail = True

    else:
        print(
            "TOKEN PREFLIGHT: PASS"
        )


overall = {
    "benchmark":
        str(BENCHMARK),

    "benchmark_sha256":
        sha256(BENCHMARK),

    "rows":
        len(rows),

    "input_token_ceiling":
        MAX_ALLOWED,

    "models":
        all_summaries,
}

(
    OUT_DIR
    / "full_token_preflight_v3.json"
).write_text(
    json.dumps(
        overall,
        indent=2,
    ),
    encoding="utf-8",
)


print()
print("=" * 100)
print("FINAL TOKEN PREFLIGHT SUMMARY")
print("=" * 100)

for x in all_summaries:
    print(
        f"{x['model_short_name']:16s} "
        f"max={x['max_tokens']:5d}  "
        f">8k={x['count_gt_8000']:4d}  "
        f">10k={x['count_gt_10000']:4d}  "
        f">12k={x['count_gt_12000']:4d}"
    )

print("=" * 100)

if global_fail:
    print(
        "PHASE 3B-4 FULL TOKEN PREFLIGHT: FAILED"
    )

    raise SystemExit(1)

print(
    "PHASE 3B-4 FULL TOKEN PREFLIGHT: PASSED"
)

print("=" * 100)
