import argparse
import gc
import hashlib
import json
import os
import random
import re
import time
from pathlib import Path

import numpy as np
import torch
import transformers

from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
)


ROOT = Path(".")

SYSTEM_PATH = Path(
    "revision_v3/phase3/contracts/"
    "system_prompt_v3.txt"
)

USER_TEMPLATE_PATH = Path(
    "revision_v3/phase3/contracts/"
    "user_prompt_template_v3.txt"
)

MODEL_PATH = Path(
    "revision_v3/phase3/contracts/"
    "model_revisions_v3.json"
)

PILOT_PATH = Path(
    "revision_v3/phase3/pilot/"
    "pilot_instances_v3_12.jsonl"
)

OUT_ROOT = Path(
    "revision_v3/phase3/outputs/pilot"
)

SEED = 42
MAX_NEW_TOKENS = 450
MAX_ALLOWED_INPUT_TOKENS = 12000


def sha256(path):
    h = hashlib.sha256()

    with path.open("rb") as f:
        for chunk in iter(
            lambda: f.read(1024 * 1024),
            b"",
        ):
            h.update(chunk)

    return h.hexdigest()


def read_jsonl(path):
    return [
        json.loads(x)
        for x in path.read_text(
            encoding="utf-8"
        ).splitlines()
        if x.strip()
    ]


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


def parse_strict_json(raw):
    try:
        obj = json.loads(
            raw.strip()
        )

        if not isinstance(obj, dict):
            return None, "not_object"

        return obj, None

    except Exception as exc:
        return None, (
            "json_parse_error:"
            + type(exc).__name__
        )


def validate_schema(
    obj,
    valid_doc_ids,
):
    errors = []

    if obj is None:
        return [
            "unparsed"
        ]

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
        value = obj[
            "expressed_confidence"
        ]

        if (
            isinstance(value, bool)
            or not isinstance(
                value,
                (int, float),
            )
        ):
            errors.append(
                "confidence_not_number"
            )
        elif not (
            0 <= float(value) <= 100
        ):
            errors.append(
                "confidence_out_of_range"
            )

    if "citations" in obj:

        if not isinstance(
            obj["citations"],
            list,
        ):
            errors.append(
                "citations_not_list"
            )

        else:
            for c in obj["citations"]:

                if not isinstance(c, str):
                    errors.append(
                        "citation_not_string"
                    )
                    continue

                if c not in valid_doc_ids:
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


def load_model(
    model_id,
    revision,
):
    tokenizer = (
        AutoTokenizer
        .from_pretrained(
            model_id,
            revision=revision,
            trust_remote_code=False,
        )
    )

    if tokenizer.pad_token_id is None:
        tokenizer.pad_token = (
            tokenizer.eos_token
        )

    model = (
        AutoModelForCausalLM
        .from_pretrained(
            model_id,
            revision=revision,
            torch_dtype=torch.float16,
            device_map="auto",
            low_cpu_mem_usage=True,
            trust_remote_code=False,
        )
    )

    model.eval()

    return tokenizer, model


def unload(
    tokenizer,
    model,
):
    del tokenizer
    del model

    gc.collect()

    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        torch.cuda.ipc_collect()


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--only_model",
        default=None,
        help=(
            "Optional short_name. "
            "Otherwise run all models."
        ),
    )

    args = parser.parse_args()

    random.seed(SEED)
    np.random.seed(SEED)
    torch.manual_seed(SEED)

    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(
            SEED
        )

    system_prompt = (
        SYSTEM_PATH.read_text(
            encoding="utf-8"
        ).strip()
    )

    user_template = (
        USER_TEMPLATE_PATH.read_text(
            encoding="utf-8"
        )
    )

    pilot = read_jsonl(
        PILOT_PATH
    )

    revisions = json.loads(
        MODEL_PATH.read_text(
            encoding="utf-8"
        )
    )

    models = revisions["models"]

    if args.only_model:
        models = [
            x for x in models
            if (
                x["short_name"]
                == args.only_model
            )
        ]

        if not models:
            raise RuntimeError(
                "Unknown --only_model "
                + args.only_model
            )

    print("=" * 88)
    print(
        "DANGERMAP-RAG PHASE 3B: "
        "SIX-MODEL GENERATION PILOT"
    )
    print("=" * 88)

    print(
        "Pilot rows:",
        len(pilot),
    )

    print(
        "Pilot SHA256:",
        sha256(PILOT_PATH),
    )

    print(
        "System prompt SHA256:",
        sha256(SYSTEM_PATH),
    )

    print(
        "User template SHA256:",
        sha256(
            USER_TEMPLATE_PATH
        ),
    )

    print(
        "torch:",
        torch.__version__,
    )

    print(
        "transformers:",
        transformers.__version__,
    )

    print(
        "CUDA:",
        torch.cuda.is_available(),
    )

    if torch.cuda.is_available():
        print(
            "GPU:",
            torch.cuda.get_device_name(0),
        )

    overall = []

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
        print("=" * 88)
        print(
            f"MODEL: {short}"
        )
        print(model_id)
        print(
            "revision:",
            revision,
        )
        print("=" * 88)

        if torch.cuda.is_available():
            before_free = (
                torch.cuda.mem_get_info()[0]
                / 1024**3
            )

            print(
                "GPU free before load:",
                f"{before_free:.2f} GiB",
            )

        start_load = time.time()

        tokenizer, model = (
            load_model(
                model_id,
                revision,
            )
        )

        load_seconds = (
            time.time()
            - start_load
        )

        max_context_seen = 0
        model_rows = []

        for idx, instance in enumerate(
            pilot,
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
                return_tensors="pt",
                add_special_tokens=False,
                truncation=False,
            )

            input_tokens = int(
                encoded[
                    "input_ids"
                ].shape[-1]
            )

            max_context_seen = max(
                max_context_seen,
                input_tokens,
            )

            if (
                input_tokens
                > MAX_ALLOWED_INPUT_TOKENS
            ):
                raise RuntimeError(
                    f"{short} / "
                    f"{instance['instance_id']}: "
                    f"{input_tokens} input tokens "
                    f"> {MAX_ALLOWED_INPUT_TOKENS}"
                )

            device = next(
                model.parameters()
            ).device

            encoded = {
                k: v.to(device)
                for k, v in
                encoded.items()
            }

            start = time.time()

            with torch.inference_mode():
                generated = model.generate(
                    **encoded,
                    max_new_tokens=(
                        MAX_NEW_TOKENS
                    ),
                    do_sample=False,
                    pad_token_id=(
                        tokenizer.pad_token_id
                    ),
                    eos_token_id=(
                        tokenizer.eos_token_id
                    ),
                )

            seconds = (
                time.time()
                - start
            )

            new_tokens = generated[
                0,
                encoded[
                    "input_ids"
                ].shape[-1]:,
            ]

            raw = tokenizer.decode(
                new_tokens,
                skip_special_tokens=True,
            ).strip()

            parsed, parse_error = (
                parse_strict_json(
                    raw
                )
            )

            valid_doc_ids = {
                str(d["doc_id"])
                for d in
                instance[
                    "evidence_docs"
                ]
            }

            schema_errors = (
                validate_schema(
                    parsed,
                    valid_doc_ids,
                )
            )

            strict_valid = (
                parse_error is None
                and not schema_errors
            )

            row = {
                "model_short_name":
                    short,

                "model_id":
                    model_id,

                "model_revision":
                    revision,

                "instance_id":
                    instance[
                        "instance_id"
                    ],

                "base_id":
                    instance[
                        "base_id"
                    ],

                "dataset":
                    instance[
                        "dataset"
                    ],

                "condition":
                    instance[
                        "condition"
                    ],

                "input_tokens":
                    input_tokens,

                "output_tokens":
                    int(
                        new_tokens.shape[-1]
                    ),

                "generation_seconds":
                    seconds,

                "raw_output":
                    raw,

                "parsed_output":
                    parsed,

                "parse_error":
                    parse_error,

                "schema_errors":
                    schema_errors,

                "strict_json_valid":
                    strict_valid,
            }

            model_rows.append(row)
            overall.append(row)

            print(
                f"[{idx:02d}/12] "
                f"{instance['dataset']:10s} "
                f"{instance['condition']:14s} "
                f"in={input_tokens:5d} "
                f"out={row['output_tokens']:4d} "
                f"json={'OK' if strict_valid else 'FAIL'} "
                f"{seconds:.2f}s"
            )

        out_file = (
            OUT_ROOT
            / f"{short}_pilot_v3.jsonl"
        )

        with out_file.open(
            "w",
            encoding="utf-8",
        ) as f:

            for row in model_rows:
                f.write(
                    json.dumps(
                        row,
                        ensure_ascii=False,
                    )
                    + "\n"
                )

        valid_count = sum(
            x["strict_json_valid"]
            for x in model_rows
        )

        summary = {
            "model_short_name":
                short,

            "model_id":
                model_id,

            "revision":
                revision,

            "pilot_rows":
                len(model_rows),

            "strict_json_valid":
                valid_count,

            "json_valid_rate":
                valid_count
                / len(model_rows),

            "max_input_tokens":
                max_context_seen,

            "load_seconds":
                load_seconds,

            "mean_generation_seconds":
                float(
                    np.mean([
                        x[
                            "generation_seconds"
                        ]
                        for x in model_rows
                    ])
                ),
        }

        (
            OUT_ROOT
            / f"{short}_pilot_summary_v3.json"
        ).write_text(
            json.dumps(
                summary,
                indent=2,
            ),
            encoding="utf-8",
        )

        print()
        print(
            json.dumps(
                summary,
                indent=2,
            )
        )

        unload(
            tokenizer,
            model,
        )

    total_valid = sum(
        x["strict_json_valid"]
        for x in overall
    )

    total = len(overall)

    summary = {
        "total_generations":
            total,

        "strict_json_valid":
            total_valid,

        "strict_json_valid_rate":
            (
                total_valid / total
                if total
                else 0.0
            ),
    }

    (
        OUT_ROOT
        / "pilot_overall_summary_v3.json"
    ).write_text(
        json.dumps(
            summary,
            indent=2,
        ),
        encoding="utf-8",
    )

    print()
    print("=" * 88)
    print("PILOT OVERALL")
    print("=" * 88)

    print(
        json.dumps(
            summary,
            indent=2,
        )
    )

    print("=" * 88)

    if total_valid != total:
        print(
            "PHASE 3B PILOT: "
            "NEEDS REVIEW"
        )
    else:
        print(
            "PHASE 3B PILOT: PASSED"
        )

    print("=" * 88)


if __name__ == "__main__":
    main()
