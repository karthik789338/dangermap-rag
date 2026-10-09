import argparse
import gc
import hashlib
import json
import os
import random
import time
from pathlib import Path

import numpy as np
import torch
import transformers

from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
)


BENCHMARK = Path(
    "revision_v3/data/"
    "dangermap_instances_v3_1_12k.jsonl"
)

EXPECTED_BENCHMARK_SHA = (
    "e36d0ca8a239b4efa5848d30f4a7a217"
    "ebf0c3309d508453f44f8a27fd03a0e3"
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

OUT_ROOT = Path(
    "revision_v3/phase3/outputs/full"
)

RESULT_ROOT = Path(
    "revision_v3/phase3/results/full"
)

CHECKPOINT_ROOT = Path(
    "revision_v3/phase3/checkpoints/full"
)


SEED = 42
MAX_NEW_TOKENS = 1024
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
    rows = []

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
                rows.append(
                    json.loads(line)
                )

            except Exception as exc:
                raise RuntimeError(
                    f"Invalid JSONL in {path} "
                    f"at line {line_no}: {exc}"
                )

    return rows


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


def strict_json_parse(raw):
    try:
        obj = json.loads(
            raw.strip()
        )

        if not isinstance(
            obj,
            dict,
        ):
            return None, (
                "not_object"
            )

        return obj, None

    except Exception as exc:
        return None, (
            "json_parse_error:"
            + type(exc).__name__
        )


def strict_schema_errors(
    obj,
    valid_doc_ids,
):
    if obj is None:
        return [
            "unparsed"
        ]

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


def completed_ids_from_output(path):
    if not path.exists():
        return set()

    completed = set()

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
                row = json.loads(
                    line
                )

            except Exception as exc:
                raise RuntimeError(
                    f"Corrupt resume file "
                    f"{path} line {line_no}: "
                    f"{exc}"
                )

            instance_id = (
                row.get(
                    "instance_id"
                )
            )

            if not instance_id:
                raise RuntimeError(
                    f"Missing instance_id in "
                    f"{path} line {line_no}"
                )

            if instance_id in completed:
                raise RuntimeError(
                    "Duplicate instance_id "
                    f"in resume file: "
                    f"{instance_id}"
                )

            completed.add(
                instance_id
            )

    return completed


def atomic_write_json(
    path,
    payload,
):
    temp = path.with_suffix(
        path.suffix + ".tmp"
    )

    temp.write_text(
        json.dumps(
            payload,
            indent=2,
        ),
        encoding="utf-8",
    )

    os.replace(
        temp,
        path,
    )


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--model",
        required=True,
        help=(
            "Model short_name from "
            "model_revisions_v3.json"
        ),
    )

    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help=(
            "Optional debugging limit. "
            "Do not use for final run."
        ),
    )

    args = parser.parse_args()

    OUT_ROOT.mkdir(
        parents=True,
        exist_ok=True,
    )

    RESULT_ROOT.mkdir(
        parents=True,
        exist_ok=True,
    )

    CHECKPOINT_ROOT.mkdir(
        parents=True,
        exist_ok=True,
    )

    # ------------------------------------------------------------
    # Reproducibility checks
    # ------------------------------------------------------------
    benchmark_sha = sha256(
        BENCHMARK
    )

    if (
        benchmark_sha
        != EXPECTED_BENCHMARK_SHA
    ):
        raise RuntimeError(
            "Benchmark SHA mismatch.\n"
            f"Expected: "
            f"{EXPECTED_BENCHMARK_SHA}\n"
            f"Observed: "
            f"{benchmark_sha}"
        )

    benchmark = read_jsonl(
        BENCHMARK
    )

    if len(benchmark) != 12000:
        raise RuntimeError(
            f"Expected 12000 benchmark "
            f"instances; got "
            f"{len(benchmark)}"
        )

    instance_ids = [
        x["instance_id"]
        for x in benchmark
    ]

    if (
        len(instance_ids)
        != len(set(instance_ids))
    ):
        raise RuntimeError(
            "Benchmark contains duplicate "
            "instance IDs."
        )

    if args.limit is not None:
        benchmark = benchmark[
            :args.limit
        ]

    manifest = json.loads(
        MODEL_MANIFEST.read_text(
            encoding="utf-8"
        )
    )

    matches = [
        x for x in
        manifest["models"]
        if (
            x["short_name"]
            == args.model
        )
    ]

    if len(matches) != 1:
        raise RuntimeError(
            "Unknown or ambiguous model: "
            + args.model
        )

    model_cfg = matches[0]

    short = model_cfg[
        "short_name"
    ]

    model_id = model_cfg[
        "model_id"
    ]

    revision = model_cfg[
        "revision"
    ]

    output_path = (
        OUT_ROOT
        / f"{short}_full_v3.jsonl"
    )

    summary_path = (
        RESULT_ROOT
        / f"{short}_full_summary_v3.json"
    )

    checkpoint_path = (
        CHECKPOINT_ROOT
        / f"{short}_checkpoint_v3.json"
    )

    error_path = (
        RESULT_ROOT
        / f"{short}_generation_error_v3.json"
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

    completed = (
        completed_ids_from_output(
            output_path
        )
    )

    benchmark_target_ids = {
        x["instance_id"]
        for x in benchmark
    }

    unexpected = (
        completed
        - benchmark_target_ids
    )

    if unexpected:
        raise RuntimeError(
            "Output file contains IDs "
            "outside this run's target set. "
            f"Examples: "
            f"{sorted(unexpected)[:5]}"
        )

    remaining = [
        x for x in benchmark
        if (
            x["instance_id"]
            not in completed
        )
    ]

    random.seed(SEED)
    np.random.seed(SEED)
    torch.manual_seed(SEED)

    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(
            SEED
        )

    print("=" * 96)
    print(
        "DANGERMAP-RAG PHASE 3C: "
        "FULL GENERATION"
    )
    print("=" * 96)

    print(
        "Model:",
        short,
    )

    print(
        "Model ID:",
        model_id,
    )

    print(
        "Revision:",
        revision,
    )

    print(
        "Benchmark SHA:",
        benchmark_sha,
    )

    print(
        "Target rows:",
        len(benchmark),
    )

    print(
        "Already completed:",
        len(completed),
    )

    print(
        "Remaining:",
        len(remaining),
    )

    print(
        "Max input tokens:",
        MAX_ALLOWED_INPUT_TOKENS,
    )

    print(
        "Max new tokens:",
        MAX_NEW_TOKENS,
    )

    print(
        "do_sample:",
        False,
    )

    print(
        "Output:",
        output_path,
    )

    if not remaining:
        print()
        print(
            "Nothing to generate."
        )
        print(
            "Run final audit instead."
        )
        return

    if torch.cuda.is_available():
        print(
            "GPU:",
            torch.cuda.get_device_name(
                0
            ),
        )

        print(
            "GPU free before load:",
            f"{torch.cuda.mem_get_info()[0] / 1024**3:.2f} GiB",
        )

    print("=" * 96)

    # ------------------------------------------------------------
    # Load pinned model
    # ------------------------------------------------------------
    load_start = time.time()

    tokenizer, model = (
        load_model(
            model_id,
            revision,
        )
    )

    load_seconds = (
        time.time()
        - load_start
    )

    native_eos = (
        model.generation_config
        .eos_token_id
    )

    native_pad = (
        model.generation_config
        .pad_token_id
    )

    if native_pad is None:
        native_pad = (
            tokenizer.pad_token_id
        )

    if native_pad is None:
        if isinstance(
            native_eos,
            (list, tuple),
        ):
            native_pad = (
                native_eos[0]
            )
        else:
            native_pad = (
                native_eos
            )

    print(
        "Native EOS:",
        native_eos,
    )

    print(
        "Generation PAD:",
        native_pad,
    )

    print(
        "Load seconds:",
        f"{load_seconds:.2f}",
    )

    print("=" * 96)

    # ------------------------------------------------------------
    # Generation
    # ------------------------------------------------------------
    run_start = time.time()

    generated_this_run = 0
    strict_valid_this_run = 0
    max_input_seen = 0
    max_output_seen = 0
    max_token_hits = 0
    generation_seconds = []

    output_handle = output_path.open(
        "a",
        encoding="utf-8",
        buffering=1,
    )

    try:
        for local_idx, instance in enumerate(
            remaining,
            1,
        ):
            global_completed_before = (
                len(completed)
                + generated_this_run
            )

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

            max_input_seen = max(
                max_input_seen,
                input_tokens,
            )

            if (
                input_tokens
                > MAX_ALLOWED_INPUT_TOKENS
            ):
                raise RuntimeError(
                    f"INPUT LIMIT VIOLATION: "
                    f"{instance['instance_id']} "
                    f"has {input_tokens} tokens"
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

            try:
                with torch.inference_mode():
                    generated = (
                        model.generate(
                            **encoded,
                            max_new_tokens=(
                                MAX_NEW_TOKENS
                            ),
                            do_sample=False,
                            pad_token_id=(
                                native_pad
                            ),
                            eos_token_id=(
                                native_eos
                            ),
                        )
                    )

            except Exception as exc:
                failure = {
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

                    "completed_before_failure":
                        global_completed_before,

                    "exception_type":
                        type(exc).__name__,

                    "exception":
                        repr(exc),
                }

                atomic_write_json(
                    error_path,
                    failure,
                )

                raise

            elapsed = (
                time.time()
                - start
            )

            new_tokens = generated[
                0,
                encoded[
                    "input_ids"
                ].shape[-1]:,
            ]

            output_tokens = int(
                new_tokens.shape[-1]
            )

            max_output_seen = max(
                max_output_seen,
                output_tokens,
            )

            hit_max = (
                output_tokens
                >= MAX_NEW_TOKENS
            )

            if hit_max:
                max_token_hits += 1

            raw = tokenizer.decode(
                new_tokens,
                skip_special_tokens=True,
            ).strip()

            parsed, parse_error = (
                strict_json_parse(
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
                strict_schema_errors(
                    parsed,
                    valid_doc_ids,
                )
            )

            strict_valid = (
                parse_error is None
                and not schema_errors
            )

            row = {
                "generation_contract":
                    "DangerMap-RAG-v3-generation-1.2",

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

                "domain":
                    instance.get(
                        "domain"
                    ),

                "condition":
                    instance[
                        "condition"
                    ],

                "input_tokens":
                    input_tokens,

                "output_tokens":
                    output_tokens,

                "hit_max_new_tokens":
                    hit_max,

                "generation_seconds":
                    elapsed,

                "generation_eos_token_id":
                    native_eos,

                "generation_pad_token_id":
                    native_pad,

                "raw_output":
                    raw,

                "strict_parsed_output":
                    parsed,

                "strict_parse_error":
                    parse_error,

                "strict_schema_errors":
                    schema_errors,

                "strict_json_valid":
                    strict_valid,
            }

            output_handle.write(
                json.dumps(
                    row,
                    ensure_ascii=False,
                )
                + "\n"
            )

            output_handle.flush()

            os.fsync(
                output_handle.fileno()
            )

            generated_this_run += 1

            strict_valid_this_run += (
                int(strict_valid)
            )

            generation_seconds.append(
                elapsed
            )

            total_completed = (
                len(completed)
                + generated_this_run
            )

            if (
                local_idx == 1
                or local_idx % 100 == 0
                or local_idx
                == len(remaining)
            ):
                runtime = (
                    time.time()
                    - run_start
                )

                mean_sec = (
                    runtime
                    / generated_this_run
                )

                remaining_count = (
                    len(benchmark)
                    - total_completed
                )

                eta_hours = (
                    remaining_count
                    * mean_sec
                    / 3600
                )

                print(
                    f"[{total_completed:5d}/"
                    f"{len(benchmark):5d}] "
                    f"{instance['dataset']:10s} "
                    f"{instance['condition']:14s} "
                    f"in={input_tokens:5d} "
                    f"out={output_tokens:4d} "
                    f"strict="
                    f"{'OK' if strict_valid else 'FAIL'} "
                    f"{elapsed:6.2f}s "
                    f"ETA={eta_hours:6.2f}h",
                    flush=True,
                )

                checkpoint = {
                    "model_short_name":
                        short,

                    "model_id":
                        model_id,

                    "revision":
                        revision,

                    "benchmark_sha256":
                        benchmark_sha,

                    "target_rows":
                        len(benchmark),

                    "completed_rows":
                        total_completed,

                    "remaining_rows":
                        remaining_count,

                    "generated_this_run":
                        generated_this_run,

                    "strict_valid_this_run":
                        strict_valid_this_run,

                    "max_input_tokens_seen":
                        max_input_seen,

                    "max_output_tokens_seen":
                        max_output_seen,

                    "max_new_token_hits":
                        max_token_hits,

                    "mean_generation_seconds":
                        float(
                            np.mean(
                                generation_seconds
                            )
                        ),

                    "native_eos":
                        native_eos,

                    "generation_pad":
                        native_pad,
                }

                atomic_write_json(
                    checkpoint_path,
                    checkpoint,
                )

    finally:
        output_handle.close()

        del model
        del tokenizer

        gc.collect()

        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            torch.cuda.ipc_collect()

    # ------------------------------------------------------------
    # Completion summary
    # ------------------------------------------------------------
    final_rows = read_jsonl(
        output_path
    )

    final_ids = [
        x["instance_id"]
        for x in final_rows
    ]

    if (
        len(final_ids)
        != len(set(final_ids))
    ):
        raise RuntimeError(
            "Duplicate IDs detected "
            "after generation."
        )

    strict_total = sum(
        bool(
            x.get(
                "strict_json_valid"
            )
        )
        for x in final_rows
    )

    max_hits_total = sum(
        bool(
            x.get(
                "hit_max_new_tokens"
            )
        )
        for x in final_rows
    )

    summary = {
        "model_short_name":
            short,

        "model_id":
            model_id,

        "revision":
            revision,

        "benchmark_sha256":
            benchmark_sha,

        "output_file":
            str(output_path),

        "output_sha256":
            sha256(output_path),

        "rows":
            len(final_rows),

        "unique_instance_ids":
            len(set(final_ids)),

        "strict_json_valid":
            strict_total,

        "strict_json_valid_rate":
            strict_total
            / len(final_rows),

        "max_input_tokens":
            max(
                x["input_tokens"]
                for x in final_rows
            ),

        "max_output_tokens":
            max(
                x["output_tokens"]
                for x in final_rows
            ),

        "hit_max_new_tokens":
            max_hits_total,

        "native_eos":
            native_eos,

        "generation_pad":
            native_pad,

        "max_new_tokens":
            MAX_NEW_TOKENS,

        "do_sample":
            False,

        "load_seconds":
            load_seconds,
    }

    atomic_write_json(
        summary_path,
        summary,
    )

    print()
    print("=" * 96)
    print("MODEL GENERATION SUMMARY")
    print("=" * 96)

    print(
        json.dumps(
            summary,
            indent=2,
        )
    )

    print("=" * 96)

    expected_rows = len(
        benchmark
    )

    if (
        len(final_rows)
        != expected_rows
        or len(
            set(final_ids)
        )
        != expected_rows
    ):
        print(
            "PHASE 3C MODEL GENERATION: "
            "INCOMPLETE"
        )

        raise SystemExit(1)

    print(
        "PHASE 3C MODEL GENERATION: "
        "COMPLETE"
    )

    print("=" * 96)


if __name__ == "__main__":
    main()
