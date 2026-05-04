import argparse
import json
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Set

import torch
from tqdm import tqdm
from transformers import AutoModelForCausalLM, AutoTokenizer


SYSTEM_PROMPT = """You are a retrieval-augmented question answering system.

You must answer using only the provided evidence.

Important behavior:
- If the evidence fully supports the answer, answer directly.
- If the evidence is missing, incomplete, contradictory, stale, or does not support the answer, abstain.
- Do not use outside knowledge.
- Cite only the doc_id values provided in the evidence.
- Return valid JSON only. No markdown. No extra text.

Required JSON schema:
{
  "answer": "string",
  "abstain": true or false,
  "confidence": number from 0 to 100,
  "citations": ["doc_id_1", "doc_id_2"],
  "explanation": "brief reason grounded in the evidence"
}
"""


def read_jsonl(path: str) -> List[Dict[str, Any]]:
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def append_jsonl(path: str, row: Dict[str, Any]) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


def load_existing_ids(path: str) -> Set[str]:
    if not os.path.exists(path):
        return set()

    ids = set()
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            try:
                row = json.loads(line)
                ids.add(row["instance_id"])
            except Exception:
                pass
    return ids


def build_user_prompt(instance: Dict[str, Any], max_chars_per_doc: int) -> str:
    blocks = []

    for doc in instance.get("evidence_docs", []):
        doc_id = str(doc.get("doc_id", ""))
        title = str(doc.get("title", ""))
        text = str(doc.get("text", ""))[:max_chars_per_doc]

        blocks.append(
            f"[doc_id: {doc_id}]\n"
            f"Title: {title}\n"
            f"Text: {text}"
        )

    evidence_text = "\n\n".join(blocks)

    return f"""Question:
{instance["question"]}

Evidence:
{evidence_text}

Task:
Answer the question using only the evidence.

Return JSON only:
{{
  "answer": "...",
  "abstain": false,
  "confidence": 0,
  "citations": ["..."],
  "explanation": "..."
}}
"""


def extract_json(text: str) -> Dict[str, Any]:
    raw = text.strip()

    try:
        return json.loads(raw)
    except Exception:
        pass

    match = re.search(r"\{.*\}", raw, flags=re.DOTALL)
    if match:
        candidate = match.group(0)
        try:
            return json.loads(candidate)
        except Exception:
            pass

    return {
        "answer": "",
        "abstain": True,
        "confidence": 0,
        "citations": [],
        "explanation": "Could not parse model output as valid JSON.",
        "parse_error": True,
        "raw_output": raw[:2000]
    }


def normalize_model_output(x: Dict[str, Any]) -> Dict[str, Any]:
    answer = x.get("answer", "")
    abstain = x.get("abstain", True)
    confidence = x.get("confidence", 0)
    citations = x.get("citations", [])
    explanation = x.get("explanation", "")

    if isinstance(abstain, str):
        abstain = abstain.lower().strip() in {"true", "yes", "1"}

    try:
        confidence = float(confidence)
        if confidence <= 1:
            confidence *= 100
        confidence = max(0.0, min(100.0, confidence))
    except Exception:
        confidence = 0.0

    if not isinstance(citations, list):
        citations = [str(citations)] if citations else []

    citations = [str(c).strip() for c in citations if str(c).strip()]

    return {
        "answer": str(answer),
        "abstain": bool(abstain),
        "confidence": confidence,
        "citations": citations,
        "explanation": str(explanation),
        **{k: v for k, v in x.items() if k not in {"answer", "abstain", "confidence", "citations", "explanation"}}
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="data/processed/dangermap_instances_12k.jsonl")
    parser.add_argument("--output", default="outputs/qwen_7b_dangermap_12k_outputs.jsonl")
    parser.add_argument("--model", default="Qwen/Qwen2.5-7B-Instruct")
    parser.add_argument("--limit", type=int, default=0, help="0 means run all")
    parser.add_argument("--max_chars_per_doc", type=int, default=1800)
    parser.add_argument("--max_new_tokens", type=int, default=450)
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()

    if not torch.cuda.is_available():
        raise RuntimeError("CUDA is not available. This script is GPU-first.")

    rows = read_jsonl(args.input)
    if args.limit and args.limit > 0:
        rows = rows[:args.limit]

    done_ids = load_existing_ids(args.output) if args.resume else set()
    rows_to_run = [r for r in rows if r["instance_id"] not in done_ids]

    print("Input rows:", len(rows))
    print("Already done:", len(done_ids))
    print("Rows to run:", len(rows_to_run))
    print("Model:", args.model)

    tokenizer = AutoTokenizer.from_pretrained(args.model, trust_remote_code=True)

    model = AutoModelForCausalLM.from_pretrained(
        args.model,
        torch_dtype=torch.float16,
        device_map={"": 0},
        trust_remote_code=True,
        attn_implementation="sdpa"
    )
    model.eval()

    for instance in tqdm(rows_to_run, desc="LLM inference"):
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": build_user_prompt(instance, args.max_chars_per_doc)},
        ]

        prompt = tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )

        inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=12000).to(model.device)

        with torch.no_grad():
            output_ids = model.generate(
                **inputs,
                max_new_tokens=args.max_new_tokens,
                do_sample=False,
                pad_token_id=tokenizer.eos_token_id
            )

        generated = tokenizer.decode(
            output_ids[0][inputs["input_ids"].shape[-1]:],
            skip_special_tokens=True
        )

        parsed = normalize_model_output(extract_json(generated))

        result = {
            "instance_id": instance["instance_id"],
            "base_id": instance["base_id"],
            "domain": instance["domain"],
            "dataset": instance["dataset"],
            "task_type": instance["task_type"],
            "condition": instance["condition"],
            "question": instance["question"],
            "gold_answer": instance["gold_answer"],
            "gold_doc_ids": instance.get("gold_doc_ids", []),
            "should_abstain": instance["should_abstain"],
            "perturbation_source": instance.get("perturbation_source", ""),
            "perturbation_note": instance.get("perturbation_note", ""),
            "evidence_doc_ids": [d.get("doc_id", "") for d in instance.get("evidence_docs", [])],
            "model": args.model,
            "model_output": parsed,
            "raw_generation": generated
        }

        append_jsonl(args.output, result)

    print("\nSaved outputs to:", args.output)


if __name__ == "__main__":
    main()
