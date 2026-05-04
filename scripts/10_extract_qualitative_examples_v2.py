import argparse
import json
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd


DEFAULT_ZONES = [
    ("legal", "cuad", "missing"),
    ("legal", "casehold", "partial"),
    ("finance", "finqa", "stale"),
    ("finance", "finqa", "partial"),
    ("medical", "pubmedqa", "partial"),
    ("general", "hotpotqa", "missing"),
    ("general", "fever", "missing"),
]


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


def parse_json_list(x: Any) -> List[str]:
    if isinstance(x, list):
        return [str(v) for v in x]

    if not isinstance(x, str) or not x.strip():
        return []

    try:
        val = json.loads(x)
        if isinstance(val, list):
            return [str(v) for v in val]
    except Exception:
        pass

    return [x]


def evidence_lookup(instance: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    return {
        str(d.get("doc_id", "")): d
        for d in instance.get("evidence_docs", [])
        if str(d.get("doc_id", "")).strip()
    }


def find_doc_id(citation: str, doc_ids: List[str]) -> str:
    if citation in doc_ids:
        return citation

    for did in doc_ids:
        if citation and (citation in did or did in citation):
            return did

    return ""


def snippet(text: str, max_chars: int = 700) -> str:
    text = str(text or "").replace("\n", " ").strip()
    if len(text) <= max_chars:
        return text
    return text[:max_chars].rstrip() + " ..."


def build_example(row: pd.Series, instance: Dict[str, Any], max_evidence_chars: int) -> Dict[str, Any]:
    docs = evidence_lookup(instance)
    doc_ids = list(docs.keys())

    citations = parse_json_list(row.get("citations", "[]"))
    matched_citations = parse_json_list(row.get("matched_citations", "[]"))

    cited_docs = []

    # Prefer matched citations from scorer.
    cited_ids = matched_citations[:]

    # Fallback to raw citations.
    if not cited_ids:
        for c in citations:
            mid = find_doc_id(c, doc_ids)
            if mid:
                cited_ids.append(mid)

    for cid in cited_ids:
        d = docs.get(cid)
        if not d:
            continue

        cited_docs.append(
            {
                "doc_id": cid,
                "title": d.get("title", ""),
                "source": d.get("source", ""),
                "evidence_role": d.get("evidence_role", ""),
                "text_snippet": snippet(d.get("text", ""), max_evidence_chars),
            }
        )

    # Add gold evidence snippets separately, useful for missing/partial cases.
    gold_docs = []
    gold_ids = instance.get("gold_doc_ids", [])

    for gid in gold_ids:
        d = docs.get(gid)
        if d:
            gold_docs.append(
                {
                    "doc_id": gid,
                    "title": d.get("title", ""),
                    "source": d.get("source", ""),
                    "evidence_role": d.get("evidence_role", ""),
                    "text_snippet": snippet(d.get("text", ""), max_evidence_chars),
                }
            )

    example = {
        "instance_id": row.get("instance_id"),
        "domain": row.get("domain"),
        "dataset": row.get("dataset"),
        "condition": row.get("condition"),
        "perturbation_source": row.get("perturbation_source"),
        "question": row.get("question"),
        "gold_answer": row.get("gold_answer"),
        "model_answer": row.get("model_answer"),
        "confidence": float(row.get("confidence", 0)),
        "correctness": float(row.get("correctness", 0)),
        "danger_score": float(row.get("danger_score", 0)),
        "silent_failure": bool(row.get("silent_failure")),
        "citation_valid_wrong": bool(row.get("citation_valid_wrong")),
        "citation_appearance": float(row.get("citation_appearance", 0)),
        "citation_support_proxy": float(row.get("citation_support_proxy", 0)),
        "abstention_failure": bool(row.get("abstention_failure")),
        "raw_citations": citations,
        "cited_evidence": cited_docs,
        "gold_evidence_present_in_instance": gold_docs,
        "explanation": row.get("explanation", ""),
    }

    return example


def example_to_markdown(example: Dict[str, Any], index: int) -> str:
    lines = []

    lines.append(f"## Example {index}: {example['domain']} / {example['dataset']} / {example['condition']}")
    lines.append("")
    lines.append(f"**Instance ID:** `{example['instance_id']}`")
    lines.append("")
    lines.append(f"**Question:** {example['question']}")
    lines.append("")
    lines.append(f"**Gold answer:** {example['gold_answer']}")
    lines.append("")
    lines.append(f"**Model answer:** {example['model_answer']}")
    lines.append("")
    lines.append(
        f"**Scores:** confidence={example['confidence']:.2f}, "
        f"correctness={example['correctness']:.3f}, "
        f"danger={example['danger_score']:.3f}, "
        f"citation appearance={example['citation_appearance']:.3f}, "
        f"citation support={example['citation_support_proxy']:.3f}"
    )
    lines.append("")
    lines.append(f"**Raw citations:** `{example['raw_citations']}`")
    lines.append("")
    lines.append(f"**Why this is useful:** This is a high-risk RAG output where the model gives a confident answer under the `{example['condition']}` condition. The cited evidence should be checked against the gold answer to show whether the model relied on unsupported or misleading evidence.")
    lines.append("")

    if example["cited_evidence"]:
        lines.append("**Cited evidence snippets:**")
        lines.append("")
        for d in example["cited_evidence"]:
            lines.append(f"- `{d['doc_id']}` | role=`{d['evidence_role']}` | source=`{d['source']}`")
            lines.append(f"  - {d['text_snippet']}")
        lines.append("")

    if example["gold_evidence_present_in_instance"]:
        lines.append("**Gold evidence present in this instance:**")
        lines.append("")
        for d in example["gold_evidence_present_in_instance"]:
            lines.append(f"- `{d['doc_id']}` | role=`{d['evidence_role']}` | source=`{d['source']}`")
            lines.append(f"  - {d['text_snippet']}")
        lines.append("")
    else:
        lines.append("**Gold evidence present in this instance:** No. This is expected for missing-evidence cases.")
        lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--scored_csv",
        default="outputs/qwen_7b_full_fever_finqa_scored_v2.csv",
    )
    parser.add_argument(
        "--instances",
        default="data/processed/dangermap_instances_12k_fever_finqa.jsonl",
    )
    parser.add_argument(
        "--out_jsonl",
        default="outputs/qualitative/qualitative_examples_v2.jsonl",
    )
    parser.add_argument(
        "--out_md",
        default="outputs/qualitative/qualitative_examples_v2.md",
    )
    parser.add_argument("--per_zone", type=int, default=2)
    parser.add_argument("--max_evidence_chars", type=int, default=700)
    args = parser.parse_args()

    Path(args.out_jsonl).parent.mkdir(parents=True, exist_ok=True)

    print("=" * 80)
    print("DangerMap-RAG qualitative example extractor v2")
    print("=" * 80)

    df = pd.read_csv(args.scored_csv)
    instances = read_jsonl(args.instances)
    instance_map = {r["instance_id"]: r for r in instances}

    # Keep only strong examples.
    df = df.copy()
    df["silent_failure"] = df["silent_failure"].astype(str).str.lower().eq("true")
    df["danger_score"] = pd.to_numeric(df["danger_score"], errors="coerce").fillna(0.0)
    df["confidence"] = pd.to_numeric(df["confidence"], errors="coerce").fillna(0.0)
    df["correctness"] = pd.to_numeric(df["correctness"], errors="coerce").fillna(0.0)

    selected = []

    for domain, dataset, condition in DEFAULT_ZONES:
        zone_df = df[
            (df["domain"] == domain)
            & (df["dataset"] == dataset)
            & (df["condition"] == condition)
            & (df["silent_failure"])
        ].copy()

        zone_df = zone_df.sort_values(
            ["danger_score", "confidence"],
            ascending=False,
        ).head(args.per_zone)

        for _, row in zone_df.iterrows():
            iid = row["instance_id"]
            inst = instance_map.get(iid)

            if not inst:
                continue

            selected.append(
                build_example(row, inst, max_evidence_chars=args.max_evidence_chars)
            )

    # If some zones did not have examples, fill with global top silent failures.
    if len(selected) < len(DEFAULT_ZONES) * args.per_zone:
        already = {x["instance_id"] for x in selected}

        filler_df = df[df["silent_failure"]].sort_values(
            ["danger_score", "confidence"],
            ascending=False,
        )

        for _, row in filler_df.iterrows():
            if len(selected) >= len(DEFAULT_ZONES) * args.per_zone:
                break

            iid = row["instance_id"]
            if iid in already:
                continue

            inst = instance_map.get(iid)
            if not inst:
                continue

            selected.append(
                build_example(row, inst, max_evidence_chars=args.max_evidence_chars)
            )
            already.add(iid)

    write_jsonl(args.out_jsonl, selected)

    md_parts = ["# DangerMap-RAG Qualitative Examples\n"]
    for i, ex in enumerate(selected, start=1):
        md_parts.append(example_to_markdown(ex, i))
        md_parts.append("\n---\n")

    Path(args.out_md).write_text("\n".join(md_parts), encoding="utf-8")

    print(f"Saved JSONL: {args.out_jsonl}")
    print(f"Saved Markdown: {args.out_md}")
    print(f"Examples selected: {len(selected)}")

    print("\nSelected examples:")
    for ex in selected:
        print(
            f"{ex['instance_id']} | {ex['domain']} / {ex['dataset']} / {ex['condition']} | "
            f"danger={ex['danger_score']:.3f} | conf={ex['confidence']:.1f} | corr={ex['correctness']:.3f}"
        )


if __name__ == "__main__":
    main()
