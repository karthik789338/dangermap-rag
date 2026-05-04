import argparse
import json
import random
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from datasets import load_dataset
from tqdm import tqdm


RANDOM_SEED = 42
random.seed(RANDOM_SEED)


def safe_text(x: Any) -> str:
    if x is None:
        return ""
    if isinstance(x, list):
        return " ".join(safe_text(i) for i in x)
    if isinstance(x, dict):
        return json.dumps(x, ensure_ascii=False)
    return str(x).replace("\n", " ").strip()


def clean_text(x: Any) -> str:
    s = safe_text(x)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def write_jsonl(path: str, rows: List[Dict[str, Any]]) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def choose_split(ds, preferred=("validation", "dev", "train", "test")):
    if hasattr(ds, "keys"):
        for split in preferred:
            if split in ds:
                return ds[split]
        return ds[list(ds.keys())[0]]
    return ds


def try_dataset(attempts: List[Tuple[str, Optional[str]]], cache_dir: str):
    last_error = None
    for name, config in attempts:
        try:
            print(f"  Trying {name} config={config}")
            if config is None:
                ds = load_dataset(name, cache_dir=cache_dir)
            else:
                ds = load_dataset(name, config, cache_dir=cache_dir)
            print(f"  Loaded {name} config={config}")
            return ds, name, config
        except Exception as e:
            last_error = e
            print(f"  Failed {name} config={config}: {repr(e)}")
    raise RuntimeError(f"All dataset attempts failed. Last error: {repr(last_error)}")


def make_doc(doc_id: str, title: str, text: str, role: str, source: str) -> Dict[str, Any]:
    return {
        "doc_id": doc_id,
        "title": clean_text(title)[:300],
        "text": clean_text(text),
        "source": source,
        "evidence_role": role,
    }


def make_base_item(
    base_id: str,
    domain: str,
    dataset: str,
    task_type: str,
    question: str,
    gold_answer: str,
    gold_evidence: List[Dict[str, Any]],
    candidate_distractors: Optional[List[Dict[str, Any]]] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    return {
        "base_id": base_id,
        "domain": domain,
        "dataset": dataset,
        "task_type": task_type,
        "question": clean_text(question),
        "gold_answer": clean_text(gold_answer),
        "gold_evidence": gold_evidence,
        "candidate_distractors": candidate_distractors or [],
        "metadata": metadata or {},
    }


def load_hotpotqa(n: int, cache_dir: str) -> List[Dict[str, Any]]:
    print("\nLoading HotpotQA...")
    rows = []

    ds, used_name, used_config = try_dataset(
        [
            ("hotpotqa/hotpot_qa", "distractor"),
            ("hotpot_qa", "distractor"),
        ],
        cache_dir,
    )
    split = choose_split(ds, preferred=("validation", "train"))

    for idx, row in enumerate(tqdm(split, desc="HotpotQA")):
        if len(rows) >= n:
            break

        question = clean_text(row.get("question", ""))
        answer = clean_text(row.get("answer", ""))

        if not question or not answer:
            continue

        support_pairs = set()
        sf = row.get("supporting_facts", {})
        titles_sf = sf.get("title", []) if isinstance(sf, dict) else []
        sent_ids_sf = sf.get("sent_id", []) if isinstance(sf, dict) else []

        for title, sent_id in zip(titles_sf, sent_ids_sf):
            try:
                support_pairs.add((clean_text(title), int(sent_id)))
            except Exception:
                pass

        context = row.get("context", {})
        titles = context.get("title", []) if isinstance(context, dict) else []
        sentences_list = context.get("sentences", []) if isinstance(context, dict) else []

        gold_docs = []
        distractors = []

        for c_i, (title, sentences) in enumerate(zip(titles, sentences_list)):
            title = clean_text(title)

            if not isinstance(sentences, list):
                sentences = [safe_text(sentences)]

            support_sentences = [
                clean_text(sent)
                for s_i, sent in enumerate(sentences)
                if (title, s_i) in support_pairs
            ]

            if support_sentences:
                gold_docs.append(
                    make_doc(
                        doc_id=f"hotpotqa_{idx}_gold_{c_i}",
                        title=title,
                        text=" ".join(support_sentences),
                        role="support",
                        source="hotpotqa",
                    )
                )
            else:
                distractors.append(
                    make_doc(
                        doc_id=f"hotpotqa_{idx}_dist_{c_i}",
                        title=title,
                        text=" ".join(clean_text(s) for s in sentences[:5]),
                        role="distractor",
                        source="hotpotqa",
                    )
                )

        if not gold_docs:
            continue

        rows.append(
            make_base_item(
                base_id=f"hotpotqa_{idx}",
                domain="general",
                dataset="hotpotqa",
                task_type="qa",
                question=question,
                gold_answer=answer,
                gold_evidence=gold_docs,
                candidate_distractors=distractors,
                metadata={
                    "source_loader": used_name,
                    "source_config": used_config,
                },
            )
        )

    return rows




def _read_jsonl_file(path: Path) -> List[Dict[str, Any]]:
    rows = []
    if not path.exists():
        return rows

    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))

    return rows


def _fever_title_key(title: Any) -> str:
    from urllib.parse import unquote
    t = clean_text(title)
    t = unquote(t)
    t = t.replace(" ", "_")
    return t


def _extract_fever_needed_titles(raw_items: List[Dict[str, Any]], max_scan: int) -> set:
    titles = set()

    for item in raw_items[:max_scan]:
        label = clean_text(item.get("label", ""))
        if label == "NOT ENOUGH INFO":
            continue

        evidence_sets = item.get("evidence", [])
        if not isinstance(evidence_sets, list):
            continue

        for evidence_set in evidence_sets:
            if not isinstance(evidence_set, list):
                continue

            for ev in evidence_set:
                if not isinstance(ev, list) or len(ev) < 4:
                    continue

                wiki_title = ev[2]
                sent_id = ev[3]

                if wiki_title is None or sent_id is None:
                    continue

                titles.add(_fever_title_key(wiki_title))

    return titles


def _parse_fever_lines(lines: Any) -> Dict[int, str]:
    out = {}

    if not lines:
        return out

    if isinstance(lines, list):
        iterable = lines
    else:
        iterable = str(lines).splitlines()

    for line in iterable:
        line = str(line)
        parts = line.split("\t")
        if len(parts) >= 2:
            try:
                sid = int(parts[0])
                text = parts[1].strip()
                if text:
                    out[sid] = text
            except Exception:
                continue

    return out


def _load_fever_wiki_subset(needed_titles: set, wiki_root: str = "data/raw/fever/wiki-pages") -> Dict[str, Dict[int, str]]:
    """Load only FEVER wiki pages referenced by selected claims."""
    wiki_dir = Path(wiki_root)

    if not wiki_dir.exists():
        print(f"  FEVER wiki dir not found: {wiki_dir}")
        print("  Continuing with fallback evidence text.")
        return {}

    files = sorted(wiki_dir.glob("*.jsonl"))
    if not files:
        print(f"  No FEVER wiki jsonl files found in: {wiki_dir}")
        print("  Continuing with fallback evidence text.")
        return {}

    print(f"  Loading FEVER wiki subset for {len(needed_titles)} needed titles from {len(files)} files...")

    index = {}

    for fp in tqdm(files, desc="FEVER wiki subset"):
        with open(fp, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue

                try:
                    row = json.loads(line)
                except Exception:
                    continue

                page_id = _fever_title_key(row.get("id", ""))
                if page_id not in needed_titles:
                    continue

                lines = _parse_fever_lines(row.get("lines", ""))
                if lines:
                    index[page_id] = lines

                if len(index) >= len(needed_titles):
                    break

        if len(index) >= len(needed_titles):
            break

    print(f"  FEVER wiki pages loaded: {len(index)}")
    return index


def _fever_evidence_text(item: Dict[str, Any], wiki_index: Dict[str, Dict[int, str]]) -> str:
    evidence_sets = item.get("evidence", [])

    if not isinstance(evidence_sets, list):
        return ""

    evidence_parts = []

    # Use the first evidence set that gives us usable text.
    for evidence_set in evidence_sets:
        if not isinstance(evidence_set, list):
            continue

        parts = []

        for ev in evidence_set:
            if not isinstance(ev, list) or len(ev) < 4:
                continue

            wiki_title = ev[2]
            sent_id = ev[3]

            if wiki_title is None or sent_id is None:
                continue

            title_key = _fever_title_key(wiki_title)

            try:
                sent_id = int(sent_id)
            except Exception:
                continue

            sent_text = ""
            if title_key in wiki_index:
                sent_text = wiki_index[title_key].get(sent_id, "")

            if sent_text:
                parts.append(f"{title_key} sentence {sent_id}: {sent_text}")
            else:
                parts.append(f"Evidence page {title_key}, sentence {sent_id}.")

        if parts:
            evidence_parts = parts
            break

    return " ".join(evidence_parts)


def load_fever(n: int, cache_dir: str) -> List[Dict[str, Any]]:
    print("\nLoading FEVER from raw JSONL files...")
    rows = []

    raw_dir = Path("data/raw/fever")
    raw_items = []
    raw_items.extend(_read_jsonl_file(raw_dir / "train.jsonl"))
    raw_items.extend(_read_jsonl_file(raw_dir / "shared_task_dev.jsonl"))

    if not raw_items:
        print("Skipping FEVER: no raw files found in data/raw/fever")
        return rows

    # We scan more than n because NEI examples are skipped for now.
    max_scan = min(len(raw_items), max(5000, n * 30))
    needed_titles = _extract_fever_needed_titles(raw_items, max_scan=max_scan)
    wiki_index = _load_fever_wiki_subset(needed_titles)

    for idx, item in enumerate(tqdm(raw_items, desc="FEVER raw")):
        if len(rows) >= n:
            break

        claim = clean_text(item.get("claim", ""))
        label = clean_text(item.get("label", ""))

        if not claim or not label:
            continue

        # For this RAG benchmark version, skip NEI because it has no gold evidence text.
        if label == "NOT ENOUGH INFO":
            continue

        evidence_text = _fever_evidence_text(item, wiki_index)

        if not evidence_text:
            continue

        item_id = clean_text(item.get("id", f"fever_{idx}"))

        rows.append(
            make_base_item(
                base_id=f"fever_{idx}",
                domain="general",
                dataset="fever",
                task_type="claim_verification",
                question=f"Verify this claim: {claim}",
                gold_answer=label,
                gold_evidence=[
                    make_doc(
                        doc_id=f"fever_{idx}_gold_0",
                        title=f"FEVER evidence for claim {item_id}",
                        text=evidence_text,
                        role="support",
                        source="fever",
                    )
                ],
                candidate_distractors=[],
                metadata={
                    "source_loader": "raw_jsonl",
                    "source_config": "data/raw/fever",
                    "label": label,
                    "claim_id": item_id,
                },
            )
        )

    return rows

def load_pubmedqa(n: int, cache_dir: str) -> List[Dict[str, Any]]:
    print("\nLoading PubMedQA...")
    rows = []

    ds, used_name, used_config = try_dataset(
        [
            ("qiaojin/PubMedQA", "pqa_labeled"),
            ("bigbio/pubmed_qa", "pubmed_qa_labeled_source"),
        ],
        cache_dir,
    )
    split = choose_split(ds, preferred=("train", "validation"))

    for idx, row in enumerate(tqdm(split, desc="PubMedQA")):
        if len(rows) >= n:
            break

        question = clean_text(row.get("question", ""))
        final_decision = clean_text(row.get("final_decision", row.get("answer", "")))

        if not question or not final_decision:
            continue

        docs = []
        context = row.get("context", {})

        if isinstance(context, dict):
            contexts = context.get("contexts", [])
            labels = context.get("labels", [])

            for c_i, ctx in enumerate(contexts):
                label = labels[c_i] if c_i < len(labels) else "ABSTRACT"
                docs.append(
                    make_doc(
                        doc_id=f"pubmedqa_{idx}_ctx_{c_i}",
                        title=f"PubMed abstract section: {label}",
                        text=ctx,
                        role="support",
                        source="pubmedqa",
                    )
                )
        else:
            docs.append(
                make_doc(
                    doc_id=f"pubmedqa_{idx}_ctx_0",
                    title="PubMedQA context",
                    text=context,
                    role="support",
                    source="pubmedqa",
                )
            )

        if not docs:
            long_answer = clean_text(row.get("long_answer", ""))
            if long_answer:
                docs.append(
                    make_doc(
                        doc_id=f"pubmedqa_{idx}_ctx_0",
                        title="PubMedQA long answer",
                        text=long_answer,
                        role="support",
                        source="pubmedqa",
                    )
                )

        if not docs:
            continue

        rows.append(
            make_base_item(
                base_id=f"pubmedqa_{idx}",
                domain="medical",
                dataset="pubmedqa",
                task_type="biomedical_qa",
                question=question,
                gold_answer=final_decision,
                gold_evidence=docs,
                candidate_distractors=[],
                metadata={
                    "long_answer": clean_text(row.get("long_answer", "")),
                    "source_loader": used_name,
                    "source_config": used_config,
                },
            )
        )

    return rows


def load_cuad(n: int, cache_dir: str) -> List[Dict[str, Any]]:
    print("\nLoading CUAD...")
    rows = []

    try:
        ds, used_name, used_config = try_dataset(
            [
                ("dvgodoy/CUAD_v1_Contract_Understanding_clause_classification", None),
                ("theatticusproject/cuad", None),
            ],
            cache_dir,
        )
    except Exception as e:
        print("Skipping CUAD:", repr(e))
        return rows

    split = choose_split(ds, preferred=("train", "validation", "test"))
    seen = set()

    for idx, row in enumerate(tqdm(split, desc="CUAD")):
        if len(rows) >= n:
            break

        keys = set(row.keys())

        label = clean_text(
            row.get(
                "label",
                row.get("clause_type", row.get("category", "")),
            )
        )
        clause = clean_text(
            row.get(
                "clause",
                row.get("answer", row.get("text", "")),
            )
        )
        file_name = clean_text(
            row.get(
                "file_name",
                row.get("contract_name", row.get("title", "contract")),
            )
        )

        if not label:
            label = "contract clause"

        if not clause:
            possible_texts = []
            for k in keys:
                val = row.get(k)
                if isinstance(val, str) and len(val) > 80:
                    possible_texts.append(val)
            if possible_texts:
                clause = max(possible_texts, key=len)

        if not clause or len(clause) < 30:
            continue

        key = (file_name, label, clause[:150])
        if key in seen:
            continue
        seen.add(key)

        question = f"What text in this contract answers the clause category '{label}'?"

        rows.append(
            make_base_item(
                base_id=f"cuad_{idx}",
                domain="legal",
                dataset="cuad",
                task_type="contract_clause_qa",
                question=question,
                gold_answer=clause[:1200],
                gold_evidence=[
                    make_doc(
                        doc_id=f"cuad_{idx}_gold_0",
                        title=f"{file_name} | {label}",
                        text=clause,
                        role="support",
                        source="cuad",
                    )
                ],
                candidate_distractors=[],
                metadata={
                    "source_loader": used_name,
                    "source_config": used_config,
                },
            )
        )

    return rows


def load_casehold(n: int, cache_dir: str) -> List[Dict[str, Any]]:
    print("\nLoading CaseHOLD via LexGLUE...")
    rows = []

    try:
        ds, used_name, used_config = try_dataset(
            [
                ("coastalcph/lex_glue", "case_hold"),
            ],
            cache_dir,
        )
    except Exception as e:
        print("Skipping CaseHOLD:", repr(e))
        return rows

    split = choose_split(ds, preferred=("train", "validation", "test"))

    for idx, row in enumerate(tqdm(split, desc="CaseHOLD")):
        if len(rows) >= n:
            break

        context = clean_text(row.get("context", row.get("prompt", "")))
        label = row.get("label", row.get("answer", None))
        endings = row.get("endings", row.get("choices", []))

        if isinstance(endings, str):
            endings = [endings]

        if not context or not endings:
            continue

        try:
            label_idx = int(label)
            correct = clean_text(endings[label_idx])
        except Exception:
            correct = clean_text(label)

        if not correct:
            continue

        question = f"Based on the legal context, what is the correct holding? Context: {context}"

        distractors = []
        for j, ending in enumerate(endings):
            ending = clean_text(ending)
            if ending and ending != correct:
                distractors.append(
                    make_doc(
                        doc_id=f"casehold_{idx}_choice_{j}",
                        title=f"CaseHOLD incorrect option {j}",
                        text=ending,
                        role="distractor",
                        source="casehold",
                    )
                )

        rows.append(
            make_base_item(
                base_id=f"casehold_{idx}",
                domain="legal",
                dataset="casehold",
                task_type="legal_multiple_choice",
                question=question,
                gold_answer=correct,
                gold_evidence=[
                    make_doc(
                        doc_id=f"casehold_{idx}_gold_0",
                        title="CaseHOLD legal context",
                        text=context + " Correct holding: " + correct,
                        role="support",
                        source="casehold",
                    )
                ],
                candidate_distractors=distractors,
                metadata={
                    "source_loader": used_name,
                    "source_config": used_config,
                },
            )
        )

    return rows


def table_to_text(table: Any) -> str:
    if not table:
        return ""

    if isinstance(table, str):
        return table

    lines = []

    if isinstance(table, list):
        for row in table:
            if isinstance(row, list):
                lines.append(" | ".join(clean_text(x) for x in row))
            elif isinstance(row, dict):
                lines.append(" | ".join(f"{k}: {clean_text(v)}" for k, v in row.items()))
            else:
                lines.append(clean_text(row))

    elif isinstance(table, dict):
        for k, v in table.items():
            lines.append(f"{k}: {clean_text(v)}")

    return "\n".join(lines)




def _load_finqa_raw_files(raw_dir: str = "data/raw/finqa") -> List[Dict[str, Any]]:
    rows = []
    raw_path = Path(raw_dir)

    for name in ["train.json", "dev.json", "test.json"]:
        fp = raw_path / name
        if not fp.exists():
            continue

        print(f"  Reading raw FinQA file: {fp}")
        with open(fp, "r", encoding="utf-8") as f:
            data = json.load(f)

        if isinstance(data, list):
            rows.extend(data)
        elif isinstance(data, dict):
            for key in ["data", "examples", "items"]:
                if key in data and isinstance(data[key], list):
                    rows.extend(data[key])
                    break

    return rows


def _finqa_supporting_facts_text(item: Dict[str, Any]) -> str:
    pre_text = item.get("pre_text", [])
    post_text = item.get("post_text", [])
    table = item.get("table", [])

    qa = item.get("qa", {})
    gold_inds = qa.get("gold_inds", {}) if isinstance(qa, dict) else {}

    selected_parts = []

    if gold_inds:
        selected_parts.append("Gold supporting fact indices: " + clean_text(gold_inds))

    if isinstance(pre_text, list):
        selected_parts.extend(clean_text(x) for x in pre_text[:8] if clean_text(x))
    elif pre_text:
        selected_parts.append(clean_text(pre_text))

    table_text = table_to_text(table)
    if table_text:
        selected_parts.append("Financial table:\n" + table_text)

    if isinstance(post_text, list):
        selected_parts.extend(clean_text(x) for x in post_text[:8] if clean_text(x))
    elif post_text:
        selected_parts.append(clean_text(post_text))

    return "\n".join(x for x in selected_parts if x)


def load_finqa(n: int, cache_dir: str) -> List[Dict[str, Any]]:
    print("\nLoading FinQA from raw JSON files...")
    rows = []

    raw_items = _load_finqa_raw_files("data/raw/finqa")

    if not raw_items:
        print("Skipping FinQA: no raw files found in data/raw/finqa")
        return rows

    for idx, item in enumerate(tqdm(raw_items, desc="FinQA raw")):
        if len(rows) >= n:
            break

        qa = item.get("qa", {})
        if not isinstance(qa, dict):
            continue

        question = clean_text(qa.get("question", ""))
        answer = clean_text(
            qa.get(
                "exe_ans",
                qa.get("answer", qa.get("program", ""))
            )
        )

        if not question or not answer:
            continue

        context_text = _finqa_supporting_facts_text(item)

        if not context_text:
            continue

        item_id = clean_text(item.get("id", f"finqa_raw_{idx}"))

        rows.append(
            make_base_item(
                base_id=f"finqa_{idx}",
                domain="finance",
                dataset="finqa",
                task_type="financial_numerical_qa",
                question=question,
                gold_answer=answer,
                gold_evidence=[
                    make_doc(
                        doc_id=f"finqa_{idx}_gold_0",
                        title=f"FinQA report item {item_id}",
                        text=context_text,
                        role="support",
                        source="finqa",
                    )
                ],
                candidate_distractors=[],
                metadata={
                    "source_loader": "raw_json",
                    "source_config": "data/raw/finqa",
                    "program": clean_text(qa.get("program", "")),
                    "gold_inds": clean_text(qa.get("gold_inds", "")),
                },
            )
        )

    return rows



def _flatten_tatqa_answer(answer: Any) -> str:
    """Normalize TAT-QA answer objects into a string."""
    if answer is None:
        return ""

    if isinstance(answer, str):
        return clean_text(answer)

    if isinstance(answer, (int, float)):
        return clean_text(answer)

    if isinstance(answer, list):
        parts = []
        for item in answer:
            item_text = _flatten_tatqa_answer(item)
            if item_text:
                parts.append(item_text)
        return "; ".join(parts)

    if isinstance(answer, dict):
        preferred_keys = [
            "answer",
            "text",
            "value",
            "number",
            "spans",
            "span",
            "answer_text",
            "final_answer",
        ]

        for key in preferred_keys:
            if key in answer:
                val = _flatten_tatqa_answer(answer.get(key))
                if val:
                    return val

        parts = []
        for _, value in answer.items():
            val = _flatten_tatqa_answer(value)
            if val:
                parts.append(val)
        return "; ".join(parts)

    return clean_text(answer)


def _tatqa_questions_to_list(questions: Any) -> List[Dict[str, Any]]:
    """Handle TAT-QA questions whether stored as list-of-dicts or dict-of-lists."""
    if questions is None:
        return []

    if isinstance(questions, list):
        out = []
        for q in questions:
            if isinstance(q, dict):
                out.append(q)
        return out

    if isinstance(questions, dict):
        keys = list(questions.keys())
        if not keys:
            return []

        lengths = []
        for k in keys:
            v = questions.get(k)
            if isinstance(v, list):
                lengths.append(len(v))

        if not lengths:
            return [questions]

        n = max(lengths)
        out = []

        for i in range(n):
            q = {}
            for k in keys:
                v = questions.get(k)
                if isinstance(v, list):
                    q[k] = v[i] if i < len(v) else None
                else:
                    q[k] = v
            out.append(q)

        return out

    return []


def _tatqa_paragraphs_to_text(paragraphs: Any) -> str:
    """Normalize TAT-QA paragraph structures into text."""
    if not paragraphs:
        return ""

    parts = []

    if isinstance(paragraphs, str):
        return clean_text(paragraphs)

    if isinstance(paragraphs, list):
        for p_item in paragraphs:
            if isinstance(p_item, dict):
                text = clean_text(
                    p_item.get("text", p_item.get("paragraph", p_item.get("content", "")))
                )
                if text:
                    parts.append(text)
            else:
                text = clean_text(p_item)
                if text:
                    parts.append(text)

    elif isinstance(paragraphs, dict):
        if "text" in paragraphs:
            text_val = paragraphs.get("text")
            if isinstance(text_val, list):
                parts.extend(clean_text(x) for x in text_val if clean_text(x))
            else:
                parts.append(clean_text(text_val))
        else:
            for _, value in paragraphs.items():
                text = clean_text(value)
                if text:
                    parts.append(text)

    return " ".join(parts)

def load_tatqa(n: int, cache_dir: str) -> List[Dict[str, Any]]:
    print("\nLoading TAT-QA...")
    rows = []

    try:
        ds, used_name, used_config = try_dataset(
            [
                ("next-tat/TAT-QA", None),
                ("tatqa", None),
            ],
            cache_dir,
        )
    except Exception as e:
        print("Skipping TAT-QA:", repr(e))
        return rows

    split = choose_split(ds, preferred=("train", "validation", "test"))

    for idx, row in enumerate(tqdm(split, desc="TAT-QA")):
        if len(rows) >= n:
            break

        table_text = table_to_text(row.get("table", []))
        paragraph_text = _tatqa_paragraphs_to_text(
            row.get("paragraphs", row.get("text", row.get("context", "")))
        )

        base_context_parts = []
        if paragraph_text:
            base_context_parts.append("Paragraph evidence:\n" + paragraph_text)
        if table_text:
            base_context_parts.append("Financial table:\n" + table_text)

        base_context = "\n\n".join(base_context_parts).strip()

        # Preferred path: document-level row with nested questions.
        nested_questions = _tatqa_questions_to_list(row.get("questions", None))

        if nested_questions:
            for q_i, qrow in enumerate(nested_questions):
                if len(rows) >= n:
                    break

                question = clean_text(qrow.get("question", qrow.get("query", "")))

                answer = _flatten_tatqa_answer(
                    qrow.get(
                        "answer",
                        qrow.get("answers", qrow.get("gold_answer", ""))
                    )
                )

                if not question or not answer:
                    continue

                facts = qrow.get("facts", qrow.get("evidence", []))
                facts_text = clean_text(facts)

                derivation = clean_text(qrow.get("derivation", ""))

                evidence_parts = []
                if facts_text:
                    evidence_parts.append("Question-specific facts:\n" + facts_text)
                if derivation:
                    evidence_parts.append("Derivation:\n" + derivation)
                if base_context:
                    evidence_parts.append(base_context)

                context_text = "\n\n".join(evidence_parts).strip()

                if not context_text:
                    continue

                rows.append(
                    make_base_item(
                        base_id=f"tatqa_{idx}_{q_i}",
                        domain="finance",
                        dataset="tatqa",
                        task_type="table_text_financial_qa",
                        question=question,
                        gold_answer=answer,
                        gold_evidence=[
                            make_doc(
                                doc_id=f"tatqa_{idx}_{q_i}_gold_0",
                                title=f"TAT-QA document {idx}, question {q_i}",
                                text=context_text,
                                role="support",
                                source="tatqa",
                            )
                        ],
                        candidate_distractors=[],
                        metadata={
                            "source_loader": used_name,
                            "source_config": used_config,
                            "answer_type": clean_text(qrow.get("answer_type", "")),
                            "answer_from": clean_text(qrow.get("answer_from", "")),
                            "scale": clean_text(qrow.get("scale", "")),
                        },
                    )
                )

            continue

        # Fallback path: question is top-level.
        question = clean_text(row.get("question", row.get("query", "")))
        answer = _flatten_tatqa_answer(
            row.get("answer", row.get("answers", row.get("gold_answer", "")))
        )

        if not question or not answer:
            continue

        if not base_context:
            continue

        rows.append(
            make_base_item(
                base_id=f"tatqa_{idx}",
                domain="finance",
                dataset="tatqa",
                task_type="table_text_financial_qa",
                question=question,
                gold_answer=answer,
                gold_evidence=[
                    make_doc(
                        doc_id=f"tatqa_{idx}_gold_0",
                        title=f"TAT-QA item {idx}",
                        text=base_context,
                        role="support",
                        source="tatqa",
                    )
                ],
                candidate_distractors=[],
                metadata={
                    "source_loader": used_name,
                    "source_config": used_config,
                },
            )
        )

    return rows

def take_mix(loaders, n_total, cache_dir):
    rows = []

    if not loaders:
        return rows

    per_loader = max(1, n_total // len(loaders))
    extra = n_total - per_loader * len(loaders)

    for i, loader in enumerate(loaders):
        target = per_loader + (1 if i < extra else 0)

        try:
            loaded_rows = loader(target, cache_dir)
            rows.extend(loaded_rows)
            print(f"{loader.__name__}: loaded {len(loaded_rows)} rows")
        except Exception as e:
            print(f"Loader failed: {loader.__name__}: {repr(e)}")

    if len(rows) > n_total:
        rows = rows[:n_total]

    return rows


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--cache_dir", default="data/cache")
    parser.add_argument("--per_domain", type=int, default=500)
    parser.add_argument("--out", default="data/processed/base_items_2k.jsonl")
    args = parser.parse_args()

    print("=" * 80)
    print("Building unified base items")
    print("=" * 80)
    print("Per-domain target:", args.per_domain)
    print("Output:", args.out)

    all_rows = []

    general = take_mix(
        loaders=[load_hotpotqa, load_fever],
        n_total=args.per_domain,
        cache_dir=args.cache_dir,
    )

    medical = take_mix(
        loaders=[load_pubmedqa],
        n_total=args.per_domain,
        cache_dir=args.cache_dir,
    )

    legal = take_mix(
        loaders=[load_cuad, load_casehold],
        n_total=args.per_domain,
        cache_dir=args.cache_dir,
    )

    finance = take_mix(
        loaders=[load_finqa, load_tatqa],
        n_total=args.per_domain,
        cache_dir=args.cache_dir,
    )

    all_rows.extend(general)
    all_rows.extend(medical)
    all_rows.extend(legal)
    all_rows.extend(finance)

    random.shuffle(all_rows)
    write_jsonl(args.out, all_rows)

    print("\nSaved:", args.out)
    print("Total base items:", len(all_rows))

    counts = {}
    for row in all_rows:
        key = (row["domain"], row["dataset"])
        counts[key] = counts.get(key, 0) + 1

    print("\nCounts:")
    for key, val in sorted(counts.items()):
        print(key, val)


if __name__ == "__main__":
    main()
