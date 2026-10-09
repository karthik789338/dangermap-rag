import argparse
import hashlib
import importlib.util
import json
import random
import re
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List

from tqdm import tqdm


RANDOM_SEED = 42
FULL_SCAN_N = 10**9


def load_v2_module():
    path = Path("scripts/02_build_base_items.py")

    spec = importlib.util.spec_from_file_location(
        "dangermap_v2_base",
        path
    )

    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot import {path}")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    return module


v2 = load_v2_module()


# ---------------------------------------------------------------------
# Source split policy
# ---------------------------------------------------------------------

def choose_split_v3(
    ds,
    preferred=None,
):
    """
    Revision-v3 split policy.

    The original v2 loaders pass their own preferred split order.
    For reproducibility, v3 ignores those loader-specific preferences
    and applies one frozen benchmark policy:

        validation -> dev -> train -> test

    This prevents CaseHOLD and TAT-QA from silently falling back to
    their original train-first behavior.
    """
    if hasattr(ds, "keys"):
        fixed_priority = (
            "validation",
            "dev",
            "train",
            "test",
        )

        for split in fixed_priority:
            if split in ds:
                print(
                    f"  V3 source split: {split}"
                )
                return ds[split]

        first = list(ds.keys())[0]

        print(
            "  V3 source split fallback:",
            first,
        )

        return ds[first]

    return ds


v2.choose_split = choose_split_v3


# ---------------------------------------------------------------------
# FinQA: use DEV only, not train+dev+test concatenated
# ---------------------------------------------------------------------

def load_finqa_dev_only(
    raw_dir: str = "data/raw/finqa",
) -> List[Dict[str, Any]]:

    fp = Path(raw_dir) / "dev.json"

    if not fp.exists():
        raise FileNotFoundError(fp)

    print(f"  Reading V3 FinQA source split: {fp}")

    data = json.loads(
        fp.read_text(encoding="utf-8")
    )

    if not isinstance(data, list):
        raise RuntimeError(
            "FinQA dev.json is not a list"
        )

    return data


v2._load_finqa_raw_files = load_finqa_dev_only


# ---------------------------------------------------------------------
# FinQA: remove annotation-only gold-index text from evidence
# ---------------------------------------------------------------------

def finqa_evidence_without_annotation_artifacts(
    item: Dict[str, Any],
) -> str:

    pre_text = item.get("pre_text", [])
    post_text = item.get("post_text", [])
    table = item.get("table", [])

    selected_parts = []

    if isinstance(pre_text, list):
        selected_parts.extend(
            v2.clean_text(x)
            for x in pre_text[:8]
            if v2.clean_text(x)
        )
    elif pre_text:
        selected_parts.append(
            v2.clean_text(pre_text)
        )

    table_text = v2.table_to_text(table)

    if table_text:
        selected_parts.append(
            "Financial table:\n" + table_text
        )

    if isinstance(post_text, list):
        selected_parts.extend(
            v2.clean_text(x)
            for x in post_text[:8]
            if v2.clean_text(x)
        )
    elif post_text:
        selected_parts.append(
            v2.clean_text(post_text)
        )

    return "\n".join(
        x for x in selected_parts if x
    )


v2._finqa_supporting_facts_text = (
    finqa_evidence_without_annotation_artifacts
)


# ---------------------------------------------------------------------
# Stable sampling
# ---------------------------------------------------------------------

def dataset_seed(dataset: str) -> int:
    raw = f"{RANDOM_SEED}:{dataset}".encode(
        "utf-8"
    )

    return int(
        hashlib.sha256(raw).hexdigest()[:16],
        16,
    )


def seeded_sample(
    rows: List[Dict[str, Any]],
    n: int,
    dataset: str,
    source_split: str,
):

    if len(rows) < n:
        raise RuntimeError(
            f"{dataset}: only {len(rows)} "
            f"eligible rows; need {n}"
        )

    rng = random.Random(
        dataset_seed(dataset)
    )

    selected = rng.sample(rows, n)

    for row in selected:
        meta = row.setdefault(
            "metadata",
            {},
        )

        meta["source_split"] = source_split
        meta["sampling_strategy"] = (
            "seeded_without_replacement_"
            "from_full_eligible_split"
        )
        meta["sampling_seed"] = RANDOM_SEED
        meta["eligible_pool_size"] = len(rows)
        meta["benchmark_version"] = (
            "revision_v3"
        )

    print(
        f"  {dataset}: "
        f"eligible={len(rows):,}, "
        f"selected={len(selected):,}, "
        f"split={source_split}"
    )

    return selected, len(rows)


# ---------------------------------------------------------------------
# CaseHOLD repair
# ---------------------------------------------------------------------

def fix_casehold_item(
    item: Dict[str, Any],
) -> Dict[str, Any]:

    if not item.get("gold_evidence"):
        raise RuntimeError(
            "CaseHOLD item without evidence: "
            f"{item.get('base_id')}"
        )

    gold = v2.clean_text(
        item.get("gold_answer", "")
    )

    evidence_text = (
        item["gold_evidence"][0]
        .get("text", "")
    )

    marker = " Correct holding: "

    if marker not in evidence_text:
        raise RuntimeError(
            "Cannot locate CaseHOLD "
            "answer-leak marker in "
            f"{item['base_id']}"
        )

    context, appended_answer = (
        evidence_text.rsplit(marker, 1)
    )

    if (
        v2.clean_text(appended_answer)
        != gold
    ):
        raise RuntimeError(
            "CaseHOLD appended-answer "
            "mismatch in "
            f"{item['base_id']}"
        )

    # Recover original option indices from
    # incorrect-option document IDs.
    by_idx = {}

    for d in item.get(
        "candidate_distractors",
        [],
    ):
        m = re.search(
            r"_choice_(\d+)$",
            str(d.get("doc_id", "")),
        )

        if m:
            by_idx[int(m.group(1))] = (
                v2.clean_text(
                    d.get("text", "")
                )
            )

    n_options = len(by_idx) + 1

    missing = sorted(
        set(range(n_options))
        - set(by_idx)
    )

    if len(missing) != 1:
        raise RuntimeError(
            "Cannot recover CaseHOLD "
            "correct option index for "
            f"{item['base_id']}: "
            f"{sorted(by_idx)}"
        )

    correct_idx = missing[0]
    by_idx[correct_idx] = gold

    options = [
        by_idx[i]
        for i in range(n_options)
    ]

    labels = [
        chr(ord("A") + i)
        for i in range(n_options)
    ]

    option_text = " ".join(
        f"{label}) {text}"
        for label, text
        in zip(labels, options)
    )

    # Context is now retrieval evidence only.
    # The user query contains the choices,
    # but not the legal context.
    item["question"] = (
        "Which holding is best supported "
        "by the retrieved legal context? "
        "Choose one option. Options: "
        + option_text
    )

    # Remove explicitly appended answer.
    item["gold_evidence"][0]["text"] = (
        v2.clean_text(context)
    )

    # Incorrect MCQ choices are task options,
    # not retrieval distractor documents.
    item["candidate_distractors"] = []

    meta = item.setdefault(
        "metadata",
        {},
    )

    meta[
        "casehold_correct_option_index"
    ] = correct_idx

    meta[
        "casehold_num_options"
    ] = n_options

    meta[
        "casehold_context_removed_from_query"
    ] = True

    meta[
        "casehold_answer_removed_from_evidence"
    ] = True

    return item


# ---------------------------------------------------------------------
# TAT-QA repair
# ---------------------------------------------------------------------

def strip_tatqa_derivation(
    item: Dict[str, Any],
) -> Dict[str, Any]:

    for doc in item.get(
        "gold_evidence",
        [],
    ):

        text = str(
            doc.get("text", "")
        )

        # Remove annotated derivation while
        # retaining facts, paragraphs and table.
        cleaned = re.sub(
            r"\s*Derivation:\s*.*?"
            r"(?=\s+(?:Paragraph evidence:"
            r"|Financial table:)|$)",
            " ",
            text,
            flags=re.IGNORECASE,
        )

        cleaned = re.sub(
            r"\s+",
            " ",
            cleaned,
        ).strip()

        doc["text"] = cleaned

    item.setdefault(
        "metadata",
        {},
    )[
        "derivation_removed_from_"
        "retrieved_evidence"
    ] = True

    return item


# ---------------------------------------------------------------------
# FEVER V3
# ---------------------------------------------------------------------

def load_fever_v3(n: int):

    print(
        "\nLoading FEVER V3 from "
        "labelled shared-task development split..."
    )

    raw_path = Path(
        "data/raw/fever/"
        "shared_task_dev.jsonl"
    )

    raw_items = v2._read_jsonl_file(
        raw_path
    )

    if not raw_items:
        raise RuntimeError(
            f"No FEVER rows found at {raw_path}"
        )

    candidates = []

    for idx, item in enumerate(raw_items):

        claim = v2.clean_text(
            item.get("claim", "")
        )

        label = v2.clean_text(
            item.get("label", "")
        )

        evidence = item.get(
            "evidence",
            [],
        )

        if (
            not claim
            or label
            not in {"SUPPORTS", "REFUTES"}
        ):
            continue

        if (
            not isinstance(evidence, list)
            or not evidence
        ):
            continue

        candidates.append(
            (idx, item)
        )

    if len(candidates) < n:
        raise RuntimeError(
            "FEVER: only "
            f"{len(candidates)} "
            "eligible dev claims; "
            f"need {n}"
        )

    rng = random.Random(
        dataset_seed("fever")
    )

    selected_pairs = rng.sample(
        candidates,
        n,
    )

    selected_raw = [
        x[1]
        for x in selected_pairs
    ]

    needed_titles = (
        v2._extract_fever_needed_titles(
            selected_raw,
            max_scan=len(selected_raw),
        )
    )

    wiki_index = (
        v2._load_fever_wiki_subset(
            needed_titles
        )
    )

    rows = []

    for raw_idx, item in tqdm(
        selected_pairs,
        desc="FEVER V3 selected",
    ):

        claim = v2.clean_text(
            item.get("claim", "")
        )

        label = v2.clean_text(
            item.get("label", "")
        )

        evidence_text = (
            v2._fever_evidence_text(
                item,
                wiki_index,
            )
        )

        if not evidence_text:
            raise RuntimeError(
                "Missing FEVER evidence "
                f"for claim id={item.get('id')}"
            )

        item_id = v2.clean_text(
            item.get(
                "id",
                f"fever_dev_{raw_idx}",
            )
        )

        row = v2.make_base_item(
            base_id=f"fever_{item_id}",
            domain="general",
            dataset="fever",
            task_type="claim_verification",
            question=(
                f"Verify this claim: {claim}"
            ),
            gold_answer=label,
            gold_evidence=[
                v2.make_doc(
                    doc_id=(
                        f"fever_{item_id}"
                        "_gold_0"
                    ),
                    title=(
                        "FEVER evidence for "
                        f"claim {item_id}"
                    ),
                    text=evidence_text,
                    role="support",
                    source="fever",
                )
            ],
            candidate_distractors=[],
            metadata={
                "source_loader":
                    "raw_jsonl",
                "source_config":
                    str(raw_path),
                "source_split":
                    "shared_task_dev",
                "label":
                    label,
                "claim_id":
                    item_id,
                "sampling_strategy":
                    "seeded_without_"
                    "replacement_from_full_"
                    "eligible_split",
                "sampling_seed":
                    RANDOM_SEED,
                "eligible_pool_size":
                    len(candidates),
                "benchmark_version":
                    "revision_v3",
            },
        )

        rows.append(row)

    print(
        "  fever: "
        f"eligible={len(candidates):,}, "
        f"selected={len(rows):,}, "
        "split=shared_task_dev"
    )

    return rows, len(candidates)


# ---------------------------------------------------------------------
# Dataset construction
# ---------------------------------------------------------------------

def build_dataset(
    name: str,
    target: int,
    cache_dir: str,
):

    if name == "fever":
        return load_fever_v3(target)

    loader_map = {
        "hotpotqa": (
            v2.load_hotpotqa,
            "validation",
        ),
        "pubmedqa": (
            v2.load_pubmedqa,
            "train",
        ),
        "cuad": (
            v2.load_cuad,
            "train",
        ),
        "casehold": (
            v2.load_casehold,
            "validation",
        ),
        "finqa": (
            v2.load_finqa,
            "dev",
        ),
        "tatqa": (
            v2.load_tatqa,
            "validation",
        ),
    }

    loader, source_split = (
        loader_map[name]
    )

    # Large N disables the old first-N
    # stopping rule, allowing us to build
    # the complete eligible source pool.
    all_rows = loader(
        FULL_SCAN_N,
        cache_dir,
    )

    if name == "casehold":
        all_rows = [
            fix_casehold_item(x)
            for x in all_rows
        ]

    elif name == "tatqa":
        all_rows = [
            strip_tatqa_derivation(x)
            for x in all_rows
        ]

    return seeded_sample(
        all_rows,
        target,
        name,
        source_split,
    )


def write_jsonl(
    path: Path,
    rows: List[Dict[str, Any]],
):
    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with path.open(
        "w",
        encoding="utf-8",
    ) as f:
        for row in rows:
            f.write(
                json.dumps(
                    row,
                    ensure_ascii=False,
                )
                + "\n"
            )


def sha256(path: Path) -> str:
    h = hashlib.sha256()

    with path.open("rb") as f:
        for chunk in iter(
            lambda: f.read(1024 * 1024),
            b"",
        ):
            h.update(chunk)

    return h.hexdigest()


# ---------------------------------------------------------------------
# Quality audit
# ---------------------------------------------------------------------

def audit(
    rows: List[Dict[str, Any]],
    pools: Dict[str, int],
):

    expected = {
        "hotpotqa": 250,
        "fever": 250,
        "pubmedqa": 500,
        "cuad": 250,
        "casehold": 250,
        "finqa": 250,
        "tatqa": 250,
    }

    counts = Counter(
        x["dataset"]
        for x in rows
    )

    ids = [
        x["base_id"]
        for x in rows
    ]

    errors = []

    if len(rows) != 2000:
        errors.append(
            "Expected 2000 rows, "
            f"got {len(rows)}"
        )

    if len(ids) != len(set(ids)):
        errors.append(
            "Duplicate base_id values detected"
        )

    for ds, n in expected.items():
        if counts[ds] != n:
            errors.append(
                f"{ds}: expected {n}, "
                f"got {counts[ds]}"
            )

    # CaseHOLD leakage checks
    for x in (
        r for r in rows
        if r["dataset"] == "casehold"
    ):
        ev = " ".join(
            d.get("text", "")
            for d in x.get(
                "gold_evidence",
                [],
            )
        )

        if "Correct holding:" in ev:
            errors.append(
                "CaseHOLD answer marker "
                "remains: "
                f"{x['base_id']}"
            )
            break

        context = (
            x["gold_evidence"][0]
            .get("text", "")
            if x.get("gold_evidence")
            else ""
        )

        if (
            context
            and context
            in x.get("question", "")
        ):
            errors.append(
                "CaseHOLD context remains "
                "inside query: "
                f"{x['base_id']}"
            )
            break

    # TAT-QA leakage check
    for x in (
        r for r in rows
        if r["dataset"] == "tatqa"
    ):
        ev = " ".join(
            d.get("text", "")
            for d in x.get(
                "gold_evidence",
                [],
            )
        )

        if "Derivation:" in ev:
            errors.append(
                "TAT-QA derivation remains: "
                f"{x['base_id']}"
            )
            break

    # FinQA annotation artifact check
    for x in (
        r for r in rows
        if r["dataset"] == "finqa"
    ):
        ev = " ".join(
            d.get("text", "")
            for d in x.get(
                "gold_evidence",
                [],
            )
        )

        if (
            "Gold supporting fact indices:"
            in ev
        ):
            errors.append(
                "FinQA annotation artifact "
                "remains: "
                f"{x['base_id']}"
            )
            break

    return counts, errors


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--cache_dir",
        default="data/cache",
    )

    parser.add_argument(
        "--out",
        default=(
            "revision_v3/data/"
            "base_items_v3_2k.jsonl"
        ),
    )

    parser.add_argument(
        "--manifest",
        default=(
            "revision_v3/phase1b/"
            "base_items_v3_manifest.json"
        ),
    )

    args = parser.parse_args()

    quotas = [
        ("hotpotqa", 250),
        ("fever", 250),
        ("pubmedqa", 500),
        ("cuad", 250),
        ("casehold", 250),
        ("finqa", 250),
        ("tatqa", 250),
    ]

    print("=" * 80)
    print(
        "DANGERMAP-RAG PHASE 1B-1: "
        "V3 BASE BENCHMARK"
    )
    print("=" * 80)

    print(
        "Sampling seed:",
        RANDOM_SEED,
    )

    all_rows = []
    pool_sizes = {}

    for dataset, target in quotas:

        print()
        print("=" * 80)
        print(
            f"{dataset}: target={target}"
        )
        print("=" * 80)

        selected, pool_size = (
            build_dataset(
                dataset,
                target,
                args.cache_dir,
            )
        )

        all_rows.extend(selected)

        pool_sizes[dataset] = (
            pool_size
        )

    # Deterministic final ordering.
    random.Random(
        RANDOM_SEED
    ).shuffle(all_rows)

    counts, errors = audit(
        all_rows,
        pool_sizes,
    )

    if errors:

        print()
        print(
            "PHASE 1B-1 AUDIT: FAILED"
        )

        for e in errors:
            print(" -", e)

        raise SystemExit(1)

    out_path = Path(args.out)

    write_jsonl(
        out_path,
        all_rows,
    )

    manifest = {
        "benchmark_version":
            "revision_v3",

        "random_seed":
            RANDOM_SEED,

        "sampling_strategy":
            "seeded_without_replacement_"
            "from_full_eligible_split",

        "total_base_items":
            len(all_rows),

        "dataset_counts":
            dict(sorted(counts.items())),

        "eligible_pool_sizes":
            pool_sizes,

        "source_splits": {
            "hotpotqa":
                "validation",

            "fever":
                "shared_task_dev",

            "pubmedqa":
                "train (pqa_labeled)",

            "cuad":
                "train",

            "casehold":
                "validation",

            "finqa":
                "dev",

            "tatqa":
                "validation",
        },

        "construction_fixes": [
            (
                "seeded sampling from the "
                "complete eligible source split"
            ),
            (
                "CaseHOLD answer removed "
                "from retrieved evidence"
            ),
            (
                "CaseHOLD legal context "
                "removed from query; "
                "answer choices retained"
            ),
            (
                "CaseHOLD incorrect choices "
                "removed from retrieval "
                "distractor pool"
            ),
            (
                "FinQA gold-index annotation "
                "artifact removed from "
                "retrieved evidence"
            ),
            (
                "TAT-QA derivation annotation "
                "removed from retrieved evidence"
            ),
        ],

        "output":
            str(out_path),

        "sha256":
            sha256(out_path),
    }

    manifest_path = Path(
        args.manifest
    )

    manifest_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    manifest_path.write_text(
        json.dumps(
            manifest,
            indent=2,
        ),
        encoding="utf-8",
    )

    print()
    print("Counts:")

    for ds, n in sorted(
        counts.items()
    ):
        print(
            f"  {ds:12s}: "
            f"{n:4d} / "
            f"pool {pool_sizes[ds]:,}"
        )

    print()
    print("Output  :", out_path)
    print(
        "SHA256  :",
        manifest["sha256"],
    )
    print(
        "Manifest:",
        manifest_path,
    )

    print("=" * 80)
    print("PHASE 1B-1: PASSED")
    print("=" * 80)


if __name__ == "__main__":
    main()
