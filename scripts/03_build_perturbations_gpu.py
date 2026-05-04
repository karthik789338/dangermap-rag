import argparse
import json
import random
from pathlib import Path
from typing import Any, Dict, List

import numpy as np
import torch
from sentence_transformers import SentenceTransformer
from tqdm import tqdm


RANDOM_SEED = 42
random.seed(RANDOM_SEED)
np.random.seed(RANDOM_SEED)


CONDITIONS = ["clean", "missing", "partial", "noisy", "contradictory", "stale"]


def read_jsonl(path: str) -> List[Dict[str, Any]]:
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def write_jsonl(path: str, rows: List[Dict[str, Any]]) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def clean_doc(doc: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "doc_id": str(doc.get("doc_id", "")),
        "title": str(doc.get("title", "")),
        "text": str(doc.get("text", "")),
        "source": str(doc.get("source", "")),
        "evidence_role": str(doc.get("evidence_role", "")),
    }


def truncate_text(text: str, max_words: int) -> str:
    words = str(text or "").split()
    if len(words) <= max_words:
        return str(text or "")
    return " ".join(words[:max_words])


def make_doc(doc_id: str, title: str, text: str, role: str, source: str) -> Dict[str, Any]:
    return {
        "doc_id": doc_id,
        "title": title,
        "text": text,
        "source": source,
        "evidence_role": role
    }


def answer_family(ans: str) -> str:
    a = str(ans or "").lower().strip()
    if a in {"yes", "no", "maybe"}:
        return "ynm"
    if any(ch.isdigit() for ch in a):
        return "numeric"
    return "text"


def opposite_answer(ans: str, fallback_pool: List[str]) -> str:
    a = str(ans or "").lower().strip()

    if a == "yes":
        return "no"
    if a == "no":
        return "yes"
    if a == "maybe":
        return random.choice(["yes", "no"])

    candidates = [
        x for x in fallback_pool
        if x and str(x).lower().strip() != a and len(str(x).strip()) < 300
    ]

    if candidates:
        return random.choice(candidates)

    return "a different answer"


def make_contradictory_doc(base: Dict[str, Any], answer_pool: List[str]) -> Dict[str, Any]:
    wrong = opposite_answer(base.get("gold_answer", ""), answer_pool)
    q = base.get("question", "")
    text = (
        f"This retrieved source discusses the same question: {q} "
        f"However, it states that the answer is '{wrong}', which conflicts with other available evidence."
    )
    return make_doc(
        doc_id=f"{base['base_id']}__contradictory_doc",
        title="Plausible conflicting evidence",
        text=text,
        role="contradictory",
        source="synthetic_controlled_contradiction"
    )


def make_stale_doc(base: Dict[str, Any], answer_pool: List[str]) -> Dict[str, Any]:
    old = opposite_answer(base.get("gold_answer", ""), answer_pool)
    q = base.get("question", "")
    text = (
        f"Older source snapshot for the question '{q}' reported the answer as '{old}'. "
        f"This source may be outdated or superseded by newer evidence."
    )
    return make_doc(
        doc_id=f"{base['base_id']}__stale_doc",
        title="Older potentially stale evidence snapshot",
        text=text,
        role="stale",
        source="synthetic_controlled_stale"
    )


def collect_doc_pool(base_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    pool = []

    for item in base_items:
        for d in item.get("gold_evidence", []):
            d = clean_doc(d)
            if len(d["text"]) > 30:
                d["owner_base_id"] = item["base_id"]
                d["owner_domain"] = item["domain"]
                d["owner_dataset"] = item["dataset"]
                pool.append(d)

        for d in item.get("candidate_distractors", []):
            d = clean_doc(d)
            if len(d["text"]) > 30:
                d["owner_base_id"] = item["base_id"]
                d["owner_domain"] = item["domain"]
                d["owner_dataset"] = item["dataset"]
                pool.append(d)

    return pool


def embed_texts(model, texts: List[str], batch_size: int) -> torch.Tensor:
    emb = model.encode(
        texts,
        batch_size=batch_size,
        convert_to_tensor=True,
        normalize_embeddings=True,
        show_progress_bar=True
    )
    return emb


def semantic_distractors(
    base_items: List[Dict[str, Any]],
    doc_pool: List[Dict[str, Any]],
    model_name: str,
    batch_size: int,
    top_k: int,
    device: str
) -> Dict[str, List[Dict[str, Any]]]:

    print("\nLoading embedding model:", model_name)
    model = SentenceTransformer(model_name, device=device)

    questions = [x["question"] for x in base_items]
    doc_texts = [
        (d.get("title", "") + "\n" + d.get("text", ""))[:3000]
        for d in doc_pool
    ]

    print("\nEmbedding questions...")
    q_emb = embed_texts(model, questions, batch_size)

    print("\nEmbedding document pool...")
    d_emb = embed_texts(model, doc_texts, batch_size)

    distractors_by_base = {}

    print("\nSelecting semantic distractors on GPU...")
    for i, item in enumerate(tqdm(base_items, desc="Semantic search")):
        query = q_emb[i:i + 1]
        scores = torch.matmul(query, d_emb.T).squeeze(0)

        # Over-fetch, then filter same item and gold docs.
        k = min(max(top_k * 8, 50), len(doc_pool))
        vals, inds = torch.topk(scores, k=k)

        selected = []
        for score, idx in zip(vals.tolist(), inds.tolist()):
            d = doc_pool[idx]
            if d.get("owner_base_id") == item["base_id"]:
                continue
            if d.get("owner_domain") != item["domain"]:
                continue

            new_d = dict(d)
            new_d["doc_id"] = f"{item['base_id']}__semantic_noise__{len(selected)}"
            new_d["evidence_role"] = "semantic_distractor"
            new_d["source"] = f"semantic_noise_from_{d.get('source', 'unknown')}"
            new_d["semantic_score"] = float(score)
            selected.append(new_d)

            if len(selected) >= top_k:
                break

        distractors_by_base[item["base_id"]] = selected

    return distractors_by_base


def build_instance(
    base: Dict[str, Any],
    condition: str,
    evidence_docs: List[Dict[str, Any]],
    should_abstain: bool,
    perturbation_source: str,
    note: str,
    max_docs: int,
    max_chars_per_doc: int
) -> Dict[str, Any]:

    cleaned_docs = []
    for d_i, d in enumerate(evidence_docs[:max_docs]):
        d = clean_doc(d)
        text = d["text"][:max_chars_per_doc]
        d["text"] = text
        if not d["doc_id"]:
            d["doc_id"] = f"{base['base_id']}__{condition}__doc_{d_i}"
        cleaned_docs.append(d)

    return {
        "instance_id": f"{base['base_id']}__{condition}",
        "base_id": base["base_id"],
        "domain": base["domain"],
        "dataset": base["dataset"],
        "task_type": base["task_type"],
        "condition": condition,
        "question": base["question"],
        "gold_answer": base["gold_answer"],
        "evidence_docs": cleaned_docs,
        "gold_doc_ids": [d.get("doc_id", "") for d in base.get("gold_evidence", [])],
        "should_abstain": should_abstain,
        "perturbation_source": perturbation_source,
        "perturbation_note": note,
        "metadata": {
            "answer_family": answer_family(base.get("gold_answer", "")),
            "base_metadata": base.get("metadata", {})
        }
    }


def build_all_instances(
    base_items: List[Dict[str, Any]],
    semantic_noise: Dict[str, List[Dict[str, Any]]],
    max_docs: int,
    max_chars_per_doc: int
) -> List[Dict[str, Any]]:

    all_answers_by_domain = {}
    for b in base_items:
        all_answers_by_domain.setdefault(b["domain"], []).append(b.get("gold_answer", ""))

    instances = []

    for base in tqdm(base_items, desc="Building perturbations"):
        gold_docs = [clean_doc(d) for d in base.get("gold_evidence", [])]
        local_distractors = [clean_doc(d) for d in base.get("candidate_distractors", [])]
        sem_noise = semantic_noise.get(base["base_id"], [])

        if not gold_docs:
            continue

        answer_pool = all_answers_by_domain.get(base["domain"], [])

        clean_docs = gold_docs + local_distractors[:2] + sem_noise[:2]

        missing_docs = local_distractors[:3] + sem_noise[:max_docs]
        if not missing_docs:
            missing_docs = sem_noise[:max_docs]

        partial_docs = []
        for i, d in enumerate(gold_docs):
            partial_docs.append(
                make_doc(
                    doc_id=f"{base['base_id']}__partial_gold_{i}",
                    title=d.get("title", "") + " | partial excerpt",
                    text=truncate_text(d.get("text", ""), max_words=45),
                    role="partial_support",
                    source=d.get("source", "") + "_partial"
                )
            )
        partial_docs += sem_noise[:3]

        noisy_docs = gold_docs + sem_noise[:max_docs]

        contradictory_docs = gold_docs + [make_contradictory_doc(base, answer_pool)] + sem_noise[:2]

        stale_docs = gold_docs + [make_stale_doc(base, answer_pool)] + sem_noise[:2]

        condition_specs = {
            "clean": {
                "docs": clean_docs,
                "should_abstain": False,
                "source": "natural_gold_plus_retrieval",
                "note": "Correct supporting evidence is present."
            },
            "missing": {
                "docs": missing_docs,
                "should_abstain": True,
                "source": "controlled_gold_removed",
                "note": "Gold evidence is removed; only distractors/noise remain."
            },
            "partial": {
                "docs": partial_docs,
                "should_abstain": True,
                "source": "controlled_partial_gold",
                "note": "Only incomplete evidence is present."
            },
            "noisy": {
                "docs": noisy_docs,
                "should_abstain": False,
                "source": "natural_gold_plus_semantic_noise",
                "note": "Gold evidence is present but mixed with semantic noise."
            },
            "contradictory": {
                "docs": contradictory_docs,
                "should_abstain": True,
                "source": "synthetic_controlled_contradiction",
                "note": "Gold evidence is mixed with plausible conflicting evidence."
            },
            "stale": {
                "docs": stale_docs,
                "should_abstain": True,
                "source": "synthetic_controlled_stale",
                "note": "Gold evidence is mixed with older potentially superseded evidence."
            },
        }

        for condition in CONDITIONS:
            spec = condition_specs[condition]
            instances.append(
                build_instance(
                    base,
                    condition,
                    spec["docs"],
                    spec["should_abstain"],
                    spec["source"],
                    spec["note"],
                    max_docs=max_docs,
                    max_chars_per_doc=max_chars_per_doc
                )
            )

    return instances


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--base_items", default="data/processed/base_items_2k.jsonl")
    parser.add_argument("--out", default="data/processed/dangermap_instances_12k.jsonl")
    parser.add_argument("--embedding_model", default="BAAI/bge-base-en-v1.5")
    parser.add_argument("--batch_size", type=int, default=128)
    parser.add_argument("--top_k_noise", type=int, default=8)
    parser.add_argument("--max_docs", type=int, default=6)
    parser.add_argument("--max_chars_per_doc", type=int, default=1800)
    parser.add_argument("--device", default="cuda")
    args = parser.parse_args()

    if args.device == "cuda" and not torch.cuda.is_available():
        raise RuntimeError("CUDA requested but not available.")

    base_items = read_jsonl(args.base_items)
    print("Loaded base items:", len(base_items))

    doc_pool = collect_doc_pool(base_items)
    print("Document pool size:", len(doc_pool))

    if not doc_pool:
        raise RuntimeError("Document pool is empty.")

    semantic_noise = semantic_distractors(
        base_items=base_items,
        doc_pool=doc_pool,
        model_name=args.embedding_model,
        batch_size=args.batch_size,
        top_k=args.top_k_noise,
        device=args.device
    )

    instances = build_all_instances(
        base_items=base_items,
        semantic_noise=semantic_noise,
        max_docs=args.max_docs,
        max_chars_per_doc=args.max_chars_per_doc
    )

    write_jsonl(args.out, instances)

    print("\nSaved instances:", args.out)
    print("Total instances:", len(instances))

    counts = {}
    for r in instances:
        key = (r["domain"], r["condition"])
        counts[key] = counts.get(key, 0) + 1

    print("\nCounts by domain and condition:")
    for key, val in sorted(counts.items()):
        print(key, val)


if __name__ == "__main__":
    main()
