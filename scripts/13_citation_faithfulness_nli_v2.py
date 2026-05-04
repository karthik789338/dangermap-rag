import argparse
import json
from pathlib import Path
from typing import Any, Dict, List

import numpy as np
import pandas as pd
import torch
from tqdm import tqdm
from transformers import AutoModelForSequenceClassification, AutoTokenizer


def read_jsonl(path: str) -> List[Dict[str, Any]]:
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def parse_json_list(x: Any) -> List[str]:
    if isinstance(x, list):
        return [str(v) for v in x if str(v).strip()]

    if not isinstance(x, str) or not x.strip():
        return []

    try:
        val = json.loads(x)
        if isinstance(val, list):
            return [str(v) for v in val if str(v).strip()]
    except Exception:
        pass

    return [x.strip()]


def ensure_bool(series: pd.Series) -> pd.Series:
    if series.dtype == bool:
        return series

    return series.astype(str).str.lower().map(
        {
            "true": True,
            "false": False,
            "1": True,
            "0": False,
            "yes": True,
            "no": False,
        }
    ).fillna(False)


def find_doc_id(citation: str, doc_ids: List[str]) -> str:
    if citation in doc_ids:
        return citation

    for did in doc_ids:
        if citation and (citation in did or did in citation):
            return did

    return ""


def truncate(text: str, max_chars: int) -> str:
    text = str(text or "").replace("\n", " ").strip()
    if len(text) <= max_chars:
        return text
    return text[:max_chars].rstrip()


def build_premise_and_hypothesis(
    row: pd.Series,
    instance: Dict[str, Any],
    max_chars_per_doc: int,
    max_total_chars: int,
) -> Dict[str, Any]:
    evidence_docs = instance.get("evidence_docs", [])
    evidence_by_id = {
        str(d.get("doc_id", "")): d
        for d in evidence_docs
        if str(d.get("doc_id", "")).strip()
    }
    evidence_ids = list(evidence_by_id.keys())

    matched = parse_json_list(row.get("matched_citations", "[]"))
    raw_citations = parse_json_list(row.get("citations", "[]"))

    cited_ids = []

    if matched:
        cited_ids = matched
    else:
        for c in raw_citations:
            mid = find_doc_id(c, evidence_ids)
            if mid:
                cited_ids.append(mid)

    cited_ids = list(dict.fromkeys(cited_ids))

    cited_parts = []
    cited_roles = []

    for cid in cited_ids:
        doc = evidence_by_id.get(cid)
        if not doc:
            continue

        title = doc.get("title", "")
        role = doc.get("evidence_role", "")
        source = doc.get("source", "")
        text = truncate(doc.get("text", ""), max_chars_per_doc)

        cited_roles.append(str(role))
        cited_parts.append(
            f"Document ID: {cid}\n"
            f"Title: {title}\n"
            f"Role: {role}\n"
            f"Source: {source}\n"
            f"Text: {text}"
        )

    premise = "\n\n".join(cited_parts)
    premise = truncate(premise, max_total_chars)

    question = str(row.get("question", ""))
    answer = str(row.get("model_answer", ""))

    # NLI works better if the model answer is transformed into a claim-like hypothesis.
    hypothesis = f"For the question: {question} The answer is: {answer}"

    return {
        "premise": premise,
        "hypothesis": hypothesis,
        "cited_ids": cited_ids,
        "cited_roles": cited_roles,
        "has_cited_evidence": bool(premise.strip()),
    }


def label_indices(model) -> Dict[str, int]:
    id2label = model.config.id2label

    normalized = {}
    for idx, label in id2label.items():
        normalized[int(idx)] = str(label).lower()

    entail_idx = None
    neutral_idx = None
    contradiction_idx = None

    for idx, label in normalized.items():
        if "entail" in label:
            entail_idx = idx
        elif "neutral" in label:
            neutral_idx = idx
        elif "contrad" in label:
            contradiction_idx = idx

    # Fallback for common MNLI order: contradiction, neutral, entailment.
    if entail_idx is None and len(normalized) == 3:
        entail_idx = 2
    if neutral_idx is None and len(normalized) == 3:
        neutral_idx = 1
    if contradiction_idx is None and len(normalized) == 3:
        contradiction_idx = 0

    return {
        "entailment": entail_idx,
        "neutral": neutral_idx,
        "contradiction": contradiction_idx,
    }


def score_batches(
    eval_rows: List[Dict[str, Any]],
    model_name: str,
    batch_size: int,
    device: str,
    max_length: int,
) -> List[Dict[str, Any]]:
    print("Loading NLI model:", model_name)
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSequenceClassification.from_pretrained(model_name)

    model.to(device)
    if device == "cuda":
        model.half()

    model.eval()

    idx_map = label_indices(model)
    print("NLI label map:", model.config.id2label)
    print("Resolved indices:", idx_map)

    scored = []

    for start in tqdm(range(0, len(eval_rows), batch_size), desc="NLI scoring"):
        batch = eval_rows[start : start + batch_size]

        premises = [b["premise"] for b in batch]
        hypotheses = [b["hypothesis"] for b in batch]

        encoded = tokenizer(
            premises,
            hypotheses,
            padding=True,
            truncation=True,
            max_length=max_length,
            return_tensors="pt",
        ).to(device)

        with torch.no_grad():
            logits = model(**encoded).logits.float()
            probs = torch.softmax(logits, dim=-1).detach().cpu().numpy()

        for item, prob in zip(batch, probs):
            entail = float(prob[idx_map["entailment"]]) if idx_map["entailment"] is not None else 0.0
            neutral = float(prob[idx_map["neutral"]]) if idx_map["neutral"] is not None else 0.0
            contradiction = (
                float(prob[idx_map["contradiction"]])
                if idx_map["contradiction"] is not None
                else 0.0
            )

            item["nli_entailment"] = entail
            item["nli_neutral"] = neutral
            item["nli_contradiction"] = contradiction
            item["nli_faithful"] = entail >= 0.50 and entail >= contradiction
            item["nli_unfaithful"] = entail < 0.50
            item["nli_contradicted"] = contradiction >= 0.50 and contradiction > entail

            scored.append(item)

    return scored


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--instances", required=True)
    parser.add_argument("--scored_csv", required=True)
    parser.add_argument("--out_csv", required=True)
    parser.add_argument("--out_jsonl", required=True)
    parser.add_argument(
        "--nli_model",
        default="MoritzLaurer/DeBERTa-v3-base-mnli-fever-anli",
    )
    parser.add_argument("--batch_size", type=int, default=16)
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--max_chars_per_doc", type=int, default=1200)
    parser.add_argument("--max_total_chars", type=int, default=3500)
    parser.add_argument("--max_length", type=int, default=512)
    parser.add_argument("--device", default="cuda")
    args = parser.parse_args()

    if args.device == "cuda" and not torch.cuda.is_available():
        raise RuntimeError("CUDA requested but not available.")

    print("=" * 80)
    print("Citation faithfulness NLI judge v2")
    print("=" * 80)

    instances = read_jsonl(args.instances)
    instance_map = {r["instance_id"]: r for r in instances}

    df = pd.read_csv(args.scored_csv)

    for col in ["silent_failure", "model_abstain", "citation_valid_wrong", "abstention_failure"]:
        if col in df.columns:
            df[col] = ensure_bool(df[col])

    if args.limit and args.limit > 0:
        df = df.head(args.limit).copy()

    print("Rows to prepare:", len(df))

    prepared = []
    skipped_abstain = 0
    skipped_no_citation = 0

    for _, row in tqdm(df.iterrows(), total=len(df), desc="Preparing NLI pairs"):
        iid = row["instance_id"]
        inst = instance_map.get(iid)

        if inst is None:
            continue

        model_abstain = bool(row.get("model_abstain", False))
        if model_abstain:
            skipped_abstain += 1
            continue

        pair = build_premise_and_hypothesis(
            row,
            inst,
            max_chars_per_doc=args.max_chars_per_doc,
            max_total_chars=args.max_total_chars,
        )

        if not pair["has_cited_evidence"]:
            skipped_no_citation += 1
            continue

        prepared.append(
            {
                "instance_id": iid,
                "domain": row.get("domain"),
                "dataset": row.get("dataset"),
                "condition": row.get("condition"),
                "question": row.get("question"),
                "gold_answer": row.get("gold_answer"),
                "model_answer": row.get("model_answer"),
                "confidence": float(row.get("confidence", 0)),
                "correctness": float(row.get("correctness", 0)),
                "danger_score": float(row.get("danger_score", 0)),
                "silent_failure": bool(row.get("silent_failure", False)),
                "citation_valid_wrong": bool(row.get("citation_valid_wrong", False)),
                "citation_appearance": float(row.get("citation_appearance", 0)),
                "citation_support_proxy": float(row.get("citation_support_proxy", 0)),
                "abstention_failure": bool(row.get("abstention_failure", False)),
                "cited_ids": pair["cited_ids"],
                "cited_roles": pair["cited_roles"],
                "premise": pair["premise"],
                "hypothesis": pair["hypothesis"],
            }
        )

    print("Prepared NLI pairs:", len(prepared))
    print("Skipped abstentions:", skipped_abstain)
    print("Skipped no cited evidence:", skipped_no_citation)

    scored = score_batches(
        prepared,
        model_name=args.nli_model,
        batch_size=args.batch_size,
        device=args.device,
        max_length=args.max_length,
    )

    out_csv = Path(args.out_csv)
    out_jsonl = Path(args.out_jsonl)
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    out_jsonl.parent.mkdir(parents=True, exist_ok=True)

    # Save compact CSV without long premise/hypothesis fields.
    compact_rows = []
    for r in scored:
        compact = dict(r)
        compact.pop("premise", None)
        compact.pop("hypothesis", None)
        compact["cited_ids"] = json.dumps(compact.get("cited_ids", []), ensure_ascii=False)
        compact["cited_roles"] = json.dumps(compact.get("cited_roles", []), ensure_ascii=False)
        compact_rows.append(compact)

    pd.DataFrame(compact_rows).to_csv(out_csv, index=False)

    with open(out_jsonl, "w", encoding="utf-8") as f:
        for r in scored:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    print("Saved CSV:", out_csv)
    print("Saved JSONL:", out_jsonl)

    if scored:
        res = pd.DataFrame(compact_rows)
        print("\nOverall NLI faithfulness:")
        print("Rows scored:", len(res))
        print("Mean entailment:", res["nli_entailment"].mean())
        print("Mean contradiction:", res["nli_contradiction"].mean())
        print("NLI faithful rate:", res["nli_faithful"].mean())
        print("NLI unfaithful rate:", res["nli_unfaithful"].mean())
        print("NLI contradicted rate:", res["nli_contradicted"].mean())

        if "silent_failure" in res.columns:
            sf = res[res["silent_failure"]]
            if len(sf):
                print("\nSilent-failure subset:")
                print("Rows:", len(sf))
                print("Mean entailment:", sf["nli_entailment"].mean())
                print("NLI faithful rate:", sf["nli_faithful"].mean())
                print("NLI unfaithful rate:", sf["nli_unfaithful"].mean())
                print("NLI contradicted rate:", sf["nli_contradicted"].mean())


if __name__ == "__main__":
    main()
