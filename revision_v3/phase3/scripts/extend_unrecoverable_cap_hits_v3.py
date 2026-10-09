import argparse
import gc
import json
import os
import random
import sys
import time
from pathlib import Path

import numpy as np
import torch


SCRIPT_DIR = Path(
    "revision_v3/phase3/scripts"
)

sys.path.insert(
    0,
    str(SCRIPT_DIR),
)

from run_full_generation_v3 import (
    BENCHMARK,
    MODEL_MANIFEST,
    SYSTEM_PATH,
    USER_TEMPLATE_PATH,
    build_messages,
    load_model,
    read_jsonl,
)


FULL_ROOT = Path(
    "revision_v3/phase3/outputs/full"
)

CANON_ROOT = Path(
    "revision_v3/phase3/canonical"
)

OUT_ROOT = Path(
    "revision_v3/phase3/outputs/"
    "cap_extensions"
)

RESULT_ROOT = Path(
    "revision_v3/phase3/results/"
    "cap_extensions"
)

MAX_ORIGINAL = 1024
MAX_EXTENDED = 2048
SEED = 42


def completed_ids(path):
    if not path.exists():
        return set()

    seen = set()

    with path.open(
        "r",
        encoding="utf-8",
    ) as f:
        for line in f:
            if not line.strip():
                continue

            x = json.loads(line)

            iid = x["instance_id"]

            if iid in seen:
                raise RuntimeError(
                    f"Duplicate extension: {iid}"
                )

            seen.add(iid)

    return seen


def atomic_json(path, payload):
    tmp = path.with_suffix(
        path.suffix + ".tmp"
    )

    tmp.write_text(
        json.dumps(
            payload,
            indent=2,
        ),
        encoding="utf-8",
    )

    os.replace(
        tmp,
        path,
    )


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--model",
        required=True,
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

    manifest = json.loads(
        MODEL_MANIFEST.read_text(
            encoding="utf-8"
        )
    )

    matches = [
        x
        for x in manifest["models"]
        if x["short_name"]
        == args.model
    ]

    if len(matches) != 1:
        raise RuntimeError(
            "Unknown model: "
            + args.model
        )

    cfg = matches[0]

    short = cfg["short_name"]
    model_id = cfg["model_id"]
    revision = cfg["revision"]

    benchmark_rows = (
        read_jsonl(BENCHMARK)
    )

    benchmark = {
        x["instance_id"]: x
        for x in benchmark_rows
    }

    full_path = (
        FULL_ROOT
        / f"{short}_full_v3.jsonl"
    )

    canon_path = (
        CANON_ROOT
        / f"{short}_canonical_v3.jsonl"
    )

    full = {
        x["instance_id"]: x
        for x in read_jsonl(
            full_path
        )
    }

    canonical = {
        x["instance_id"]: x
        for x in read_jsonl(
            canon_path
        )
    }

    targets = []

    for iid, c in canonical.items():

        if (
            c["hit_max_new_tokens"]
            and not c["recoverable"]
        ):
            original = full[iid]

            if (
                original["output_tokens"]
                != MAX_ORIGINAL
            ):
                raise RuntimeError(
                    f"{iid}: expected "
                    f"{MAX_ORIGINAL} output "
                    "tokens for cap hit"
                )

            targets.append(iid)

    targets.sort()

    expected_by_model = {
        "qwen25_3b": 2,
        "qwen25_7b": 0,
        "mistral_7b": 1,
        "phi35_mini": 53,
        "granite33_8b": 2,
        "falcon3_7b": 4,
    }

    expected = expected_by_model[
        short
    ]

    if len(targets) != expected:
        raise RuntimeError(
            f"{short}: expected "
            f"{expected} targets, "
            f"found {len(targets)}"
        )

    output_path = (
        OUT_ROOT
        / f"{short}_cap_extensions_v3.jsonl"
    )

    summary_path = (
        RESULT_ROOT
        / f"{short}_cap_extension_summary_v3.json"
    )

    done = completed_ids(
        output_path
    )

    remaining = [
        iid
        for iid in targets
        if iid not in done
    ]

    print("=" * 96)
    print(
        "DANGERMAP-RAG PHASE 3D-4: "
        "DETERMINISTIC CAP EXTENSION"
    )
    print("=" * 96)

    print("Model       :", short)
    print("Targets     :", len(targets))
    print("Completed   :", len(done))
    print("Remaining   :", len(remaining))
    print(
        "Original cap:",
        MAX_ORIGINAL,
    )
    print(
        "Extended cap:",
        MAX_EXTENDED,
    )

    if not remaining:
        print(
            "No remaining extensions."
        )
        return

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

    random.seed(SEED)
    np.random.seed(SEED)
    torch.manual_seed(SEED)

    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(
            SEED
        )

    tokenizer, model = load_model(
        model_id,
        revision,
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
            native_pad = native_eos[0]
        else:
            native_pad = native_eos

    handle = output_path.open(
        "a",
        encoding="utf-8",
        buffering=1,
    )

    generated = 0
    prefix_matches = 0
    cap_2048_hits = 0

    try:
        for index, iid in enumerate(
            remaining,
            1,
        ):
            instance = benchmark[iid]
            original = full[iid]

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
                encoded["input_ids"]
                .shape[-1]
            )

            if (
                input_tokens
                != original["input_tokens"]
            ):
                raise RuntimeError(
                    f"{iid}: input-token "
                    "count changed: "
                    f"{input_tokens} vs "
                    f"{original['input_tokens']}"
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
                output = model.generate(
                    **encoded,
                    max_new_tokens=(
                        MAX_EXTENDED
                    ),
                    do_sample=False,
                    pad_token_id=(
                        native_pad
                    ),
                    eos_token_id=(
                        native_eos
                    ),
                )

            elapsed = (
                time.time() - start
            )

            new_tokens = output[
                0,
                encoded["input_ids"]
                .shape[-1]:,
            ]

            output_tokens = int(
                new_tokens.shape[-1]
            )

            # --------------------------------------------------
            # Critical reproducibility gate:
            # The first 1024 generated tokens of the new run
            # must decode exactly to the original capped output.
            # --------------------------------------------------
            if output_tokens < MAX_ORIGINAL:
                prefix_match = False
                first_1024_text = ""
            else:
                first_1024_text = (
                    tokenizer.decode(
                        new_tokens[
                            :MAX_ORIGINAL
                        ],
                        skip_special_tokens=True,
                    ).strip()
                )

                prefix_match = (
                    first_1024_text
                    == original[
                        "raw_output"
                    ].strip()
                )

            if prefix_match:
                prefix_matches += 1

            hit_2048 = (
                output_tokens
                >= MAX_EXTENDED
            )

            if hit_2048:
                cap_2048_hits += 1

            extended_raw = (
                tokenizer.decode(
                    new_tokens,
                    skip_special_tokens=True,
                ).strip()
            )

            row = {
                "model_short_name":
                    short,

                "model_id":
                    model_id,

                "model_revision":
                    revision,

                "instance_id":
                    iid,

                "base_id":
                    instance["base_id"],

                "dataset":
                    instance["dataset"],

                "condition":
                    instance["condition"],

                "input_tokens":
                    input_tokens,

                "original_output_tokens":
                    original[
                        "output_tokens"
                    ],

                "extended_output_tokens":
                    output_tokens,

                "prefix_match_1024":
                    prefix_match,

                "hit_2048_cap":
                    hit_2048,

                "generation_seconds":
                    elapsed,

                "generation_eos_token_id":
                    native_eos,

                "generation_pad_token_id":
                    native_pad,

                "original_raw_output":
                    original[
                        "raw_output"
                    ],

                "extended_raw_output":
                    extended_raw,
            }

            handle.write(
                json.dumps(
                    row,
                    ensure_ascii=False,
                )
                + "\n"
            )

            handle.flush()
            os.fsync(
                handle.fileno()
            )

            generated += 1

            print(
                f"[{index:3d}/"
                f"{len(remaining):3d}] "
                f"{iid:42s} "
                f"out={output_tokens:4d} "
                f"prefix="
                f"{'OK' if prefix_match else 'FAIL'} "
                f"cap2048="
                f"{'YES' if hit_2048 else 'NO'} "
                f"{elapsed:6.2f}s",
                flush=True,
            )

    finally:
        handle.close()

        del model
        del tokenizer

        gc.collect()

        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            torch.cuda.ipc_collect()

    final_rows = read_jsonl(
        output_path
    )

    summary = {
        "model_short_name":
            short,

        "expected_targets":
            expected,

        "extension_rows":
            len(final_rows),

        "prefix_matches_1024":
            sum(
                bool(
                    x[
                        "prefix_match_1024"
                    ]
                )
                for x in final_rows
            ),

        "prefix_mismatches_1024":
            sum(
                not bool(
                    x[
                        "prefix_match_1024"
                    ]
                )
                for x in final_rows
            ),

        "hit_2048_cap":
            sum(
                bool(
                    x["hit_2048_cap"]
                )
                for x in final_rows
            ),

        "max_extended_output_tokens":
            max(
                (
                    x[
                        "extended_output_tokens"
                    ]
                    for x in final_rows
                ),
                default=0,
            ),
    }

    atomic_json(
        summary_path,
        summary,
    )

    print()
    print(
        json.dumps(
            summary,
            indent=2,
        )
    )

    if (
        summary[
            "prefix_mismatches_1024"
        ] != 0
    ):
        raise RuntimeError(
            "PREFIX REPRODUCIBILITY "
            "GATE FAILED"
        )

    print("=" * 96)
    print(
        "CAP EXTENSION GENERATION: "
        "COMPLETE"
    )
    print("=" * 96)


if __name__ == "__main__":
    main()
