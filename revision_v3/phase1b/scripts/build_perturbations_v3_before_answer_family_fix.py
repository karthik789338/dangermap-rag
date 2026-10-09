import argparse
import hashlib
import json
import math
import random
import re
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
import torch
from sentence_transformers import SentenceTransformer
from tqdm import tqdm


SEED = 42

CONDITIONS = [
    "clean",
    "missing",
    "partial",
    "noisy",
    "contradictory",
    "stale",
]

BGE_MODEL = "BAAI/bge-base-en-v1.5"
BGE_REVISION = "a5beb1e3e68b9ab74eb54cfd186867f64f240e1a"

STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by",
    "for", "from", "has", "have", "how", "in", "is",
    "it", "of", "on", "or", "that", "the", "this",
    "to", "was", "were", "what", "when", "where",
    "which", "who", "why", "with", "using", "use",
    "does", "do", "did", "based", "retrieved",
    "evidence", "answer", "question",
}

# Audit only explicit generator-added meta-cues.
#
# Do NOT ban ordinary words such as "conflict" or "contradict":
# those legitimately occur in legal, biomedical, and factual source
# text and may also occur naturally in a benchmark question.
#
# These phrases target the problematic v2 behavior where the
# perturbation itself announced that evidence was conflicting/stale.
FORBIDDEN_SYNTHETIC_CUES = [
    "conflicts with other available evidence",
    "contradicts other available evidence",
    "this answer conflicts with",
    "this evidence contradicts",
    "may be outdated or superseded",
    "outdated or superseded",
    "this source is outdated",
    "this evidence is stale",
    "stale evidence",
    "the wrong answer is",
    "incorrect answer",
]


def read_jsonl(path):
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def write_jsonl(path, rows):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def stable_seed(*parts):
    raw = "::".join(str(x) for x in parts).encode("utf-8")
    return int(hashlib.sha256(raw).hexdigest()[:16], 16)


def rng_for(*parts):
    return random.Random(stable_seed(SEED, *parts))


def norm(x):
    return re.sub(r"\s+", " ", str(x or "")).strip()


def clean_doc(d):
    return {
        "doc_id": str(d.get("doc_id", "")),
        "title": norm(d.get("title", "")),
        "text": str(d.get("text", "")).strip(),
        "source": str(d.get("source", "")),
        "evidence_role": str(d.get("evidence_role", "")),
    }


def make_doc(doc_id, title, text, role, source):
    return {
        "doc_id": doc_id,
        "title": norm(title),
        "text": str(text or "").strip(),
        "source": source,
        "evidence_role": role,
    }


def answer_family(answer):
    a = norm(answer).lower()

    if a in {"yes", "no", "maybe"}:
        return "ynm"

    if a in {
        "supports",
        "refutes",
        "not enough information",
    }:
        return "fever_label"

    if re.search(r"[-+]?\d", a):
        return "numeric"

    return "text"


def content_tokens(text):
    toks = re.findall(
        r"[a-z0-9]+",
        str(text or "").lower(),
    )

    return [
        t for t in toks
        if len(t) >= 3
        and t not in STOPWORDS
    ]


def overlap_score(question, text):
    q = set(content_tokens(question))

    if not q:
        return 0.0

    t = set(content_tokens(text))

    return len(q & t) / len(q)


def numeric_values(text):
    from decimal import Decimal, InvalidOperation

    vals = []

    for raw in re.findall(
        r"[-+]?\$?\d[\d,]*(?:\.\d+)?%?",
        str(text or ""),
    ):
        cleaned = (
            raw.replace("$", "")
               .replace(",", "")
               .replace("%", "")
        )

        try:
            vals.append(
                Decimal(cleaned).normalize()
            )
        except InvalidOperation:
            pass

    return vals


def answer_leak(text, answer):
    family = answer_family(answer)

    # Labels such as yes/no and SUPPORTS/REFUTES cannot be
    # validated through literal answer-string matching.
    if family in {
        "ynm",
        "fever_label",
    }:
        return False

    text_n = norm(text).lower()
    ans_n = norm(answer).lower()

    if family == "text":
        return (
            len(ans_n) >= 4
            and ans_n in text_n
        )

    # Numeric comparison is value based:
    # 257, 257.0 and 257.00 are equivalent.
    answer_nums = set(
        numeric_values(answer)
    )

    text_nums = set(
        numeric_values(text)
    )

    return bool(
        answer_nums
        and answer_nums & text_nums
    )


def split_segments(text):
    text = str(text or "").strip()

    if not text:
        return []

    lines = [
        norm(x)
        for x in text.splitlines()
        if norm(x)
    ]

    if not lines:
        lines = [norm(text)]

    out = []

    for line in lines:

        if len(line) <= 420:
            out.append(line)
            continue

        parts = re.split(
            r"(?<=[.!?])\s+",
            line,
        )

        parts = [
            norm(x)
            for x in parts
            if norm(x)
        ]

        if len(parts) == 1:
            words = line.split()

            parts = [
                " ".join(words[i:i + 70])
                for i in range(
                    0,
                    len(words),
                    70,
                )
            ]

        out.extend(parts)

    return out


def priority(question, answer, segment):
    score = overlap_score(
        question,
        segment,
    )

    if answer_leak(
        segment,
        answer,
    ):
        score += 4.0

    gold_nums = set(
        re.findall(
            r"\d+(?:\.\d+)?",
            norm(answer),
        )
    )

    seg_nums = set(
        re.findall(
            r"\d+(?:\.\d+)?",
            norm(segment),
        )
    )

    if gold_nums & seg_nums:
        score += 2.0

    return score


def support_aware_clip(
    text,
    question,
    answer,
    max_chars,
):
    text = str(text or "").strip()

    if len(text) <= max_chars:
        return text

    segs = split_segments(text)

    ranked = sorted(
        range(len(segs)),
        key=lambda i: (
            priority(
                question,
                answer,
                segs[i],
            ),
            len(segs[i]),
        ),
        reverse=True,
    )

    chosen = []
    used = 0

    for idx in ranked:
        seg = segs[idx]
        cost = len(seg) + 1

        if chosen and (
            used + cost > max_chars
        ):
            continue

        if (
            not chosen
            and cost > max_chars
        ):
            chosen.append(
                (idx, seg[:max_chars])
            )
            break

        chosen.append(
            (idx, seg)
        )

        used += cost

        if used >= max_chars:
            break

    chosen.sort(
        key=lambda x: x[0]
    )

    return " ".join(
        x[1]
        for x in chosen
    )[:max_chars]


def prepared_gold(
    base,
    max_chars,
):
    docs = []

    for raw in base.get(
        "gold_evidence",
        [],
    ):
        d = clean_doc(raw)

        d["text"] = (
            support_aware_clip(
                d["text"],
                base["question"],
                base["gold_answer"],
                max_chars,
            )
        )

        if d["text"]:
            docs.append(d)

    return docs


def doc_pool(
    base_items,
    max_chars,
):
    pool = []

    for base in base_items:

        docs = (
            base.get(
                "gold_evidence",
                [],
            )
            + base.get(
                "candidate_distractors",
                [],
            )
        )

        for raw in docs:
            d = clean_doc(raw)

            if len(norm(d["text"])) < 40:
                continue

            d["text"] = (
                support_aware_clip(
                    d["text"],
                    base["question"],
                    base["gold_answer"],
                    max_chars,
                )
            )

            d["owner_base_id"] = (
                base["base_id"]
            )
            d["owner_dataset"] = (
                base["dataset"]
            )
            d["owner_domain"] = (
                base["domain"]
            )

            pool.append(d)

    return pool


def text_fingerprint(text):
    return hashlib.sha256(
        norm(text).lower().encode("utf-8")
    ).hexdigest()


def token_jaccard(a, b):
    x = set(content_tokens(a))
    y = set(content_tokens(b))

    if not x or not y:
        return 0.0

    return (
        len(x & y)
        / len(x | y)
    )


def semantic_distractors(
    base_items,
    pool,
    model,
    batch_size,
    top_k,
):
    questions = [
        x["question"]
        for x in base_items
    ]

    doc_texts = [
        (
            d["title"]
            + "\n"
            + d["text"]
        )[:4000]
        for d in pool
    ]

    print("\nEmbedding questions...")

    q_emb = model.encode(
        questions,
        batch_size=batch_size,
        convert_to_tensor=True,
        normalize_embeddings=True,
        show_progress_bar=True,
    )

    print("\nEmbedding document pool...")

    d_emb = model.encode(
        doc_texts,
        batch_size=batch_size,
        convert_to_tensor=True,
        normalize_embeddings=True,
        show_progress_bar=True,
    )

    result = {}

    print("\nSelecting semantic distractors...")

    for i, base in enumerate(
        tqdm(
            base_items,
            desc="Semantic search",
        )
    ):
        scores = torch.matmul(
            q_emb[i:i + 1],
            d_emb.T,
        ).squeeze(0)

        k = min(
            max(
                top_k * 125,
                1000,
            ),
            len(pool),
        )

        _, inds = torch.topk(
            scores,
            k=k,
        )

        target_gold_texts = [
            norm(d.get("text", ""))
            for d in base.get(
                "gold_evidence",
                [],
            )
            if norm(d.get("text", ""))
        ]

        target_gold_fps = {
            text_fingerprint(x)
            for x in target_gold_texts
        }

        same_dataset = []
        same_domain = []
        seen_fps = set()

        for idx in inds.tolist():
            d = pool[idx]

            if (
                d["owner_base_id"]
                == base["base_id"]
            ):
                continue

            candidate_text = norm(
                d["text"]
            )

            fp = text_fingerprint(
                candidate_text
            )

            # Exclude exact duplicate distractors.
            if fp in seen_fps:
                continue

            # Exclude exact copies of target support.
            if fp in target_gold_fps:
                continue

            # Exclude near-copies of target supporting evidence.
            if any(
                token_jaccard(
                    candidate_text,
                    gold_text,
                ) >= 0.85
                for gold_text
                in target_gold_texts
            ):
                continue

            # Exclude distractors that directly reveal a
            # text or numeric gold answer.
            if answer_leak(
                candidate_text,
                base["gold_answer"],
            ):
                continue

            seen_fps.add(fp)

            candidate = dict(d)

            if (
                d["owner_dataset"]
                == base["dataset"]
            ):
                same_dataset.append(
                    candidate
                )

            elif (
                d["owner_domain"]
                == base["domain"]
            ):
                same_domain.append(
                    candidate
                )

            if (
                len(same_dataset)
                + len(same_domain)
                >= top_k * 5
            ):
                break

        selected = (
            same_dataset[:top_k]
        )

        if len(selected) < top_k:
            selected += same_domain[
                :top_k - len(selected)
            ]

        if len(selected) < top_k:
            raise RuntimeError(
                base["base_id"]
                + ": insufficient "
                "non-duplicate safe "
                "semantic distractors; "
                f"found {len(selected)}, "
                f"need {top_k}"
            )

        result[
            base["base_id"]
        ] = [
            make_doc(
                doc_id=(
                    f"{base['base_id']}"
                    f"__semantic_noise__{j}"
                ),
                title=d["title"],
                text=d["text"],
                role="semantic_distractor",
                source=(
                    "semantic_noise_from_"
                    + d["owner_dataset"]
                ),
            )
            for j, d
            in enumerate(selected)
        ]

    return result


def parse_casehold_options(question):
    if "Options:" not in question:
        return []

    tail = question.split(
        "Options:",
        1,
    )[1]

    matches = re.findall(
        r"(?:^|\s)([A-Z])\)\s*"
        r"(.*?)"
        r"(?=\s+[A-Z]\)\s+|$)",
        tail,
        flags=re.DOTALL,
    )

    return [
        norm(text)
        for _, text in matches
        if norm(text)
    ]


def answer_pools(base_items):
    pools = defaultdict(list)

    for base in base_items:
        ans = norm(
            base["gold_answer"]
        )

        pools[
            (
                base["dataset"],
                answer_family(ans),
            )
        ].append(ans)

    return pools


def alternative_answer(
    base,
    pools,
    tag,
):
    gold = norm(
        base["gold_answer"]
    )

    lower = gold.lower()

    fixed = {
        "yes": "no",
        "no": "yes",
        "maybe": "no",
        "supports": "refutes",
        "refutes": "supports",
        "not enough information":
            "refutes",
    }

    if lower in fixed:
        return fixed[lower]

    if base["dataset"] == "casehold":

        options = [
            x
            for x in
            parse_casehold_options(
                base["question"]
            )
            if x != gold
        ]

        if options:
            return rng_for(
                base["base_id"],
                tag,
            ).choice(options)

    family = answer_family(gold)

    candidates = []

    for x in pools[
        (
            base["dataset"],
            family,
        )
    ]:
        x = norm(x)

        if (
            not x
            or x.lower() == lower
        ):
            continue

        if len(x) > 500:
            x = x[:500].rsplit(
                " ",
                1,
            )[0]

        candidates.append(x)

    candidates = sorted(
        set(candidates),
        key=lambda x: (
            abs(
                len(x)
                - len(gold)
            ),
            x,
        ),
    )

    if not candidates:
        raise RuntimeError(
            "No alternative answer for "
            + base["base_id"]
        )

    candidates = (
        candidates[:32]
    )

    return rng_for(
        base["base_id"],
        tag,
    ).choice(candidates)


def contradiction_doc(
    base,
    pools,
):
    alt = alternative_answer(
        base,
        pools,
        "contradiction",
    )

    text = (
        "Question recorded: "
        + base["question"]
        + "\nReported answer: "
        + alt
    )

    return (
        make_doc(
            (
                base["base_id"]
                + "__contradictory_doc"
            ),
            (
                "Independent "
                "retrieved record"
            ),
            text,
            "contradictory",
            (
                "synthetic_controlled_"
                "contradiction_v3"
            ),
        ),
        alt,
    )


def stale_doc(
    base,
    pools,
):
    alt = alternative_answer(
        base,
        pools,
        "stale",
    )

    year = rng_for(
        base["base_id"],
        "stale_year",
    ).randint(
        2010,
        2018,
    )

    text = (
        f"Snapshot date: "
        f"{year}-06-30.\n"
        f"Question recorded: "
        f"{base['question']}\n"
        f"Reported answer in this "
        f"snapshot: {alt}"
    )

    return (
        make_doc(
            (
                base["base_id"]
                + "__stale_doc"
            ),
            (
                "Archived source "
                f"snapshot ({year})"
            ),
            text,
            "stale",
            (
                "synthetic_controlled_"
                "stale_v3"
            ),
        ),
        alt,
        year,
    )


def partial_fragment(
    text,
    question,
    answer,
):
    words = norm(text).split()

    if len(words) <= 8:
        return " ".join(
            words[
                :max(
                    1,
                    len(words) // 2,
                )
            ]
        )

    n = max(
        8,
        int(
            len(words) * 0.35
        ),
    )

    n = min(
        n,
        len(words) - 1,
    )

    prefix = " ".join(
        words[:n]
    )

    suffix = " ".join(
        words[-n:]
    )

    candidates = [
        prefix,
        suffix,
    ]

    candidates.sort(
        key=lambda x: (
            answer_leak(
                x,
                answer,
            ),
            -overlap_score(
                question,
                x,
            ),
        )
    )

    return candidates[0]


def partialize_doc(
    base,
    doc,
):
    text = doc["text"]

    if (
        base["dataset"] == "tatqa"
        and "Question-specific facts:"
        in text
    ):
        cleaned = re.sub(
            r"Question-specific facts:"
            r"\s*.*?"
            r"(?=(?:Paragraph evidence:"
            r"|Financial table:)|$)",
            " ",
            text,
            flags=(
                re.IGNORECASE
                | re.DOTALL
            ),
        )

        if norm(cleaned):
            text = norm(cleaned)

    segs = split_segments(text)

    original_len = max(
        1,
        len(norm(doc["text"])),
    )

    if len(segs) <= 1:

        partial = partial_fragment(
            text,
            base["question"],
            base["gold_answer"],
        )

    else:

        ranked = sorted(
            range(len(segs)),
            key=lambda i: priority(
                base["question"],
                base["gold_answer"],
                segs[i],
            ),
            reverse=True,
        )

        remove = set()

        for i, seg in enumerate(
            segs
        ):
            if answer_leak(
                seg,
                base["gold_answer"],
            ):
                remove.add(i)

        remove.add(ranked[0])

        def retained():
            return " ".join(
                seg
                for i, seg
                in enumerate(segs)
                if i not in remove
            ).strip()

        partial = retained()

        for idx in ranked[1:]:

            ratio = (
                len(norm(partial))
                / original_len
            )

            remaining = (
                len(segs)
                - len(remove)
            )

            if (
                ratio <= 0.65
                or remaining <= 1
            ):
                break

            remove.add(idx)

            partial = retained()

        if not partial:
            partial = partial_fragment(
                text,
                base["question"],
                base["gold_answer"],
            )

    if answer_leak(
        partial,
        base["gold_answer"],
    ):
        partial = partial_fragment(
            text,
            base["question"],
            base["gold_answer"],
        )

    partial = norm(partial)

    ratio = (
        len(partial)
        / original_len
    )

    return (
        make_doc(
            (
                base["base_id"]
                + "__partial__"
                + doc["doc_id"]
            ),
            (
                doc["title"]
                + " | partial evidence"
            ),
            partial,
            "partial_support",
            (
                doc["source"]
                + "_partial_v3"
            ),
        ),
        ratio,
    )


def partial_set_ratio(
    gold_docs,
    partial_docs_list,
):
    original = sum(
        len(norm(d["text"]))
        for d in gold_docs
    )

    retained = sum(
        len(norm(d["text"]))
        for d in partial_docs_list
    )

    return (
        retained
        / max(1, original)
    )


def cap_partial_set(
    base,
    gold_docs,
    partial_docs_list,
    target_max=0.80,
):
    """
    Enforce a benchmark-level distinction between clean and partial.

    The partial condition must preserve some source evidence while
    retaining at most target_max of the original evidence volume.

    If too much evidence remains:
      1. remove the most question/answer-relevant retained document
         while at least one document remains;
      2. if a single oversized document still exceeds the threshold,
         reduce that document using partial_fragment().

    This is deterministic for a fixed base item.
    """

    work = [
        dict(d)
        for d in partial_docs_list
        if norm(d.get("text", ""))
    ]

    if not work:
        raise RuntimeError(
            "No partial evidence available for "
            + base["base_id"]
        )

    ratio = partial_set_ratio(
        gold_docs,
        work,
    )

    # Remove the most decisive retained document(s)
    # until the global evidence ratio is controlled.
    while (
        ratio > target_max
        and len(work) > 1
    ):
        remove_idx = max(
            range(len(work)),
            key=lambda i: priority(
                base["question"],
                base["gold_answer"],
                work[i]["text"],
            ),
        )

        work.pop(remove_idx)

        ratio = partial_set_ratio(
            gold_docs,
            work,
        )

    # If one retained document dominates the original evidence,
    # reduce it internally rather than accepting an almost-clean
    # partial condition.
    if ratio > target_max:
        d = dict(work[0])

        reduced = partial_fragment(
            d["text"],
            base["question"],
            base["gold_answer"],
        )

        if not norm(reduced):
            raise RuntimeError(
                "Partial reduction produced "
                "empty evidence for "
                + base["base_id"]
            )

        d["text"] = norm(reduced)

        work = [d]

        ratio = partial_set_ratio(
            gold_docs,
            work,
        )

    if not (
        0.0 < ratio <= target_max
    ):
        raise RuntimeError(
            f"{base['base_id']}: "
            f"partial ratio remained "
            f"{ratio:.6f} after capping"
        )

    return work, ratio


def fever_topic_only_partial(
    base,
    gold_docs,
):
    """
    FEVER often has one decisive evidence sentence.
    Preserve topical identity without retaining the
    claim-verifying proposition.
    """

    entities = []

    for d in gold_docs:
        text = d["text"]

        for m in re.finditer(
            r"(.+?)\s+sentence\s+\d+\s*:",
            text,
            flags=re.IGNORECASE,
        ):
            title = m.group(1)

            title = (
                title
                .replace("_", " ")
                .replace("-LRB-", "(")
                .replace("-RRB-", ")")
            )

            # Parenthetical disambiguators such as "(film)"
            # can themselves resolve some FEVER claims.
            title = re.sub(
                r"\s*\([^)]*\)\s*$",
                "",
                title,
            )

            title = norm(title)

            if title:
                entities.append(title)

    entities = list(
        dict.fromkeys(entities)
    )

    if not entities:
        entities = [
            " ".join(
                content_tokens(
                    base["question"]
                )[:8]
            )
        ]

    topic = "; ".join(
        entities[:3]
    )

    d = make_doc(
        base["base_id"]
        + "__partial_topic",
        "Retrieved topic metadata",
        topic,
        "partial_support",
        "fever_topic_only_partial_v3_1",
    )

    original = sum(
        len(norm(x["text"]))
        for x in gold_docs
    )

    ratio = (
        len(norm(d["text"]))
        / max(1, original)
    )

    return [d], ratio


def hotpot_partial(
    base,
    gold_docs,
):
    """
    Remove answer-bearing supporting hops first.
    """

    safe = [
        d for d in gold_docs
        if not answer_leak(
            d["text"],
            base["gold_answer"],
        )
    ]

    # If every hop is individually safe, break the
    # multi-hop chain by removing the most relevant hop.
    if len(safe) == len(gold_docs):

        if len(safe) > 1:
            remove_idx = max(
                range(len(safe)),
                key=lambda i:
                    overlap_score(
                        base["question"],
                        safe[i]["text"],
                    ),
            )

            safe = [
                d
                for i, d in enumerate(safe)
                if i != remove_idx
            ]

        else:
            pd, _ = partialize_doc(
                base,
                safe[0],
            )

            safe = [pd]

    if not safe:
        for d in gold_docs:
            pd, _ = partialize_doc(
                base,
                d,
            )

            if (
                norm(pd["text"])
                and not answer_leak(
                    pd["text"],
                    base["gold_answer"],
                )
            ):
                safe.append(pd)

    if not safe:
        raise RuntimeError(
            "HotpotQA decisive-support "
            "removal failed for "
            + base["base_id"]
        )

    converted = []

    for d in safe:
        converted.append(
            make_doc(
                (
                    base["base_id"]
                    + "__partial__"
                    + d["doc_id"]
                ),
                (
                    d["title"]
                    + " | retained support hop"
                ),
                d["text"],
                "partial_support",
                d["source"]
                + "_partial_v3_1",
            )
        )

    return cap_partial_set(
        base,
        gold_docs,
        converted,
    )


def pubmed_partial(
    base,
    gold_docs,
):
    """
    Prefer BACKGROUND/METHODS-like sections and remove
    RESULTS/CONCLUSIONS-like sections.
    """

    safe_labels = (
        "background",
        "objective",
        "objectives",
        "methods",
        "method",
        "design",
        "materials",
        "patients",
        "introduction",
    )

    decisive_labels = (
        "results",
        "result",
        "conclusion",
        "conclusions",
        "findings",
    )

    safe = []

    for d in gold_docs:
        title = d["title"].lower()

        if any(
            x in title
            for x in decisive_labels
        ):
            continue

        if any(
            x in title
            for x in safe_labels
        ):
            safe.append(d)

    if not safe:
        # Fallback: retain the least question-relevant half.
        ranked = sorted(
            gold_docs,
            key=lambda d:
                overlap_score(
                    base["question"],
                    d["text"],
                ),
        )

        n_keep = max(
            1,
            len(ranked) // 2,
        )

        safe = ranked[:n_keep]

    converted = [
        make_doc(
            (
                base["base_id"]
                + "__partial__"
                + d["doc_id"]
            ),
            (
                d["title"]
                + " | retained non-result section"
            ),
            d["text"],
            "partial_support",
            d["source"]
            + "_partial_v3_1",
        )
        for d in safe
    ]

    return cap_partial_set(
        base,
        gold_docs,
        converted,
    )


def financial_numeric_partial(
    base,
    gold_docs,
):
    """
    Construct partial evidence for numerical FinQA/TAT-QA items.

    Keep surrounding narrative and table labels/schema while removing
    answer-bearing numerical content. This preserves topical relevance
    without retaining the decisive value needed to compute the answer.
    """

    converted = []

    for d in gold_docs:
        original = str(
            d.get("text", "")
        ).strip()

        if not original:
            continue

        # ----------------------------------------------------------
        # 1. Separate narrative from the rendered financial table.
        # ----------------------------------------------------------
        m = re.search(
            r"\bFinancial table:\s*",
            original,
            flags=re.IGNORECASE,
        )

        if m:
            narrative = original[:m.start()]
            table_text = original[m.end():]
        else:
            narrative = original
            table_text = ""

        pieces = []

        # ----------------------------------------------------------
        # 2. Keep the most query-relevant narrative segments that
        #    do NOT expose the gold numeric answer.
        # ----------------------------------------------------------
        narrative_segments = [
            norm(seg)
            for seg in split_segments(
                narrative
            )
            if (
                norm(seg)
                and not answer_leak(
                    seg,
                    base["gold_answer"],
                )
            )
        ]

        narrative_segments = sorted(
            narrative_segments,
            key=lambda seg:
                overlap_score(
                    base["question"],
                    seg,
                ),
            reverse=True,
        )

        if narrative_segments:
            pieces.append(
                " ".join(
                    narrative_segments[:3]
                )
            )

        # ----------------------------------------------------------
        # 3. Retain only textual table labels / schema.
        #
        # Numeric data cells are deliberately omitted. This leaves
        # table topic/structure without the answer-bearing values.
        # ----------------------------------------------------------
        if table_text:
            cells = [
                norm(x)
                for x in table_text
                    .replace(
                        "\n",
                        " | ",
                    )
                    .split("|")
            ]

            safe_labels = []
            seen = set()

            for cell in cells:
                if not cell:
                    continue

                if answer_leak(
                    cell,
                    base["gold_answer"],
                ):
                    continue

                # Keep labels/descriptors, not raw numeric cells.
                if not re.search(
                    r"[A-Za-z]",
                    cell,
                ):
                    continue

                key = cell.lower()

                if key in seen:
                    continue

                seen.add(key)

                safe_labels.append(
                    cell[:220]
                )

                if len(
                    safe_labels
                ) >= 24:
                    break

            if safe_labels:
                pieces.append(
                    "Financial table labels: "
                    + " | ".join(
                        safe_labels
                    )
                )

        candidate = "\n".join(
            x
            for x in pieces
            if norm(x)
        ).strip()

        # ----------------------------------------------------------
        # 4. Fallback: choose the most question-relevant original
        #    segment that does not expose the answer.
        # ----------------------------------------------------------
        if not candidate:
            safe_segments = [
                norm(seg)
                for seg in split_segments(
                    original
                )
                if (
                    norm(seg)
                    and not answer_leak(
                        seg,
                        base["gold_answer"],
                    )
                )
            ]

            if safe_segments:
                candidate = max(
                    safe_segments,
                    key=lambda seg:
                        overlap_score(
                            base["question"],
                            seg,
                        ),
                )

        # ----------------------------------------------------------
        # 5. Last source-derived fallback: document title.
        # ----------------------------------------------------------
        if not candidate:
            title = norm(
                d.get("title", "")
            )

            if (
                title
                and not answer_leak(
                    title,
                    base["gold_answer"],
                )
            ):
                candidate = title

        if not candidate:
            continue

        # Never allow direct numeric answer leakage.
        if answer_leak(
            candidate,
            base["gold_answer"],
        ):
            continue

        converted.append(
            make_doc(
                (
                    base["base_id"]
                    + "__partial_financial__"
                    + d["doc_id"]
                ),
                (
                    d["title"]
                    + " | retained "
                    "financial context"
                ),
                candidate,
                "partial_support",
                (
                    d["source"]
                    + "_financial_partial_v3_1"
                ),
            )
        )

    if not converted:
        raise RuntimeError(
            "Financial numerical partial "
            "construction failed for "
            + base["base_id"]
        )

    work, ratio = cap_partial_set(
        base,
        gold_docs,
        converted,
    )

    leaked = [
        d["doc_id"]
        for d in work
        if answer_leak(
            d["text"],
            base["gold_answer"],
        )
    ]

    if leaked:
        raise RuntimeError(
            base["base_id"]
            + ": financial partial "
            "still exposes gold answer "
            f"in {leaked}"
        )

    return work, ratio


def partial_docs(
    base,
    gold_docs,
):
    if base["dataset"] == "fever":
        return fever_topic_only_partial(
            base,
            gold_docs,
        )

    if base["dataset"] == "hotpotqa":
        return hotpot_partial(
            base,
            gold_docs,
        )

    if base["dataset"] == "pubmedqa":
        return pubmed_partial(
            base,
            gold_docs,
        )

    if (
        base["dataset"]
        in {"finqa", "tatqa"}
        and answer_family(
            base["gold_answer"]
        ) == "numeric"
    ):
        return financial_numeric_partial(
            base,
            gold_docs,
        )

    # Remaining CUAD, CaseHOLD and non-numeric
    # FinQA/TAT-QA cases:
    # remove answer-bearing / decisive segments.
    docs = []

    for d in gold_docs:
        pd, _ = partialize_doc(
            base,
            d,
        )

        if not norm(pd["text"]):
            continue

        if answer_leak(
            pd["text"],
            base["gold_answer"],
        ):
            continue

        docs.append(pd)

    if not docs:
        raise RuntimeError(
            "Could not construct safe "
            "partial evidence for "
            + base["base_id"]
        )

    work, ratio = cap_partial_set(
        base,
        gold_docs,
        docs,
    )

    # Final literal/value-based leak check.
    if answer_family(
        base["gold_answer"]
    ) not in {
        "ynm",
        "fever_label",
    }:

        leaked = [
            d["doc_id"]
            for d in work
            if answer_leak(
                d["text"],
                base["gold_answer"],
            )
        ]

        if leaked:
            raise RuntimeError(
                base["base_id"]
                + ": partial evidence "
                "still exposes gold answer "
                f"in {leaked}"
            )

    return work, ratio


def build_instance(
    base,
    condition,
    docs,
    should_abstain,
    source,
    note,
    extra_metadata,
    max_docs,
):
    docs = [
        clean_doc(d)
        for d in docs[:max_docs]
    ]

    return {
        "instance_id": (
            f"{base['base_id']}"
            f"__{condition}"
        ),
        "base_id":
            base["base_id"],
        "domain":
            base["domain"],
        "dataset":
            base["dataset"],
        "task_type":
            base["task_type"],
        "condition":
            condition,
        "question":
            base["question"],
        "gold_answer":
            base["gold_answer"],
        "evidence_docs":
            docs,
        "gold_doc_ids": [
            str(
                d.get(
                    "doc_id",
                    "",
                )
            )
            for d in
            base.get(
                "gold_evidence",
                [],
            )
        ],
        "should_abstain":
            should_abstain,
        "perturbation_source":
            source,
        "perturbation_note":
            note,
        "metadata": {
            "benchmark_version":
                "revision_v3",
            "answer_family":
                answer_family(
                    base["gold_answer"]
                ),
            "base_metadata":
                base.get(
                    "metadata",
                    {},
                ),
            **extra_metadata,
        },
    }


def build_instances(
    base_items,
    semantic_noise,
    pools,
    max_docs,
    max_chars,
):
    rows = []

    for base in tqdm(
        base_items,
        desc="Building perturbations",
    ):

        gold = prepared_gold(
            base,
            max_chars,
        )

        if not gold:
            raise RuntimeError(
                base["base_id"]
                + ": no usable "
                "gold evidence"
            )

        noise = semantic_noise[
            base["base_id"]
        ]

        partial, ratio = (
            partial_docs(
                base,
                gold,
            )
        )

        contra, contra_alt = (
            contradiction_doc(
                base,
                pools,
            )
        )

        stale, stale_alt, year = (
            stale_doc(
                base,
                pools,
            )
        )

        specs = {
            "clean": {
                "docs":
                    gold,
                "abstain":
                    False,
                "source":
                    "gold_evidence_only_v3",
                "note":
                    "Only sufficient "
                    "supporting evidence "
                    "is provided.",
                "meta": {
                    "gold_only": True,
                },
            },

            "missing": {
                "docs":
                    noise[:max_docs],
                "abstain":
                    True,
                "source":
                    "gold_removed_"
                    "semantic_retrieval_v3",
                "note":
                    "All gold evidence "
                    "is removed.",
                "meta": {
                    "gold_removed": True,
                },
            },

            "partial": {
                "docs":
                    partial,
                "abstain":
                    True,
                "source":
                    "decisive_support_"
                    "removed_v3",
                "note":
                    "Only reduced "
                    "original support "
                    "is retained.",
                "meta": {
                    "partial_retained_ratio":
                        ratio,
                },
            },

            "noisy": {
                "docs":
                    gold
                    + noise[
                        :max(
                            0,
                            max_docs
                            - len(gold),
                        )
                    ],
                "abstain":
                    False,
                "source":
                    "gold_plus_semantic_"
                    "noise_v3",
                "note":
                    "Sufficient support "
                    "is preserved with "
                    "semantic distractors.",
                "meta": {
                    "gold_preserved":
                        True,
                },
            },

            "contradictory": {
                "docs":
                    gold
                    + [contra]
                    + noise[:2],
                "abstain":
                    True,
                "source":
                    "gold_plus_neutral_"
                    "conflicting_record_v3",
                "note":
                    "Support is mixed "
                    "with a record "
                    "asserting an "
                    "alternative answer.",
                "meta": {
                    "synthetic_"
                    "alternative_answer":
                        contra_alt,
                },
            },

            "stale": {
                "docs":
                    [stale]
                    + noise[
                        :max(
                            0,
                            max_docs - 1,
                        )
                    ],
                "abstain":
                    True,
                "source":
                    "archived_snapshot_"
                    "only_v3",
                "note":
                    "Only an archived "
                    "answer-bearing "
                    "snapshot and "
                    "non-supporting "
                    "retrievals are "
                    "available.",
                "meta": {
                    "synthetic_"
                    "alternative_answer":
                        stale_alt,
                    "snapshot_year":
                        year,
                    "reference_year":
                        2026,
                },
            },
        }

        for condition in CONDITIONS:

            s = specs[condition]

            rows.append(
                build_instance(
                    base,
                    condition,
                    s["docs"],
                    s["abstain"],
                    s["source"],
                    s["note"],
                    s["meta"],
                    max_docs,
                )
            )

    return rows


def audit(
    base_items,
    instances,
):
    errors = []

    if len(base_items) != 2000:
        errors.append(
            "Expected 2000 "
            f"base items; got "
            f"{len(base_items)}"
        )

    if len(instances) != 12000:
        errors.append(
            "Expected 12000 "
            f"instances; got "
            f"{len(instances)}"
        )

    ids = [
        x["instance_id"]
        for x in instances
    ]

    if len(ids) != len(set(ids)):
        errors.append(
            "Duplicate instance IDs"
        )

    counts = Counter(
        x["condition"]
        for x in instances
    )

    for condition in CONDITIONS:
        if counts[condition] != 2000:
            errors.append(
                f"{condition}: "
                f"{counts[condition]} "
                "instances"
            )

    by_base = defaultdict(list)

    for x in instances:
        by_base[
            x["base_id"]
        ].append(x)

    expected_conditions = sorted(
        CONDITIONS
    )

    for base in base_items:

        observed = sorted(
            x["condition"]
            for x in
            by_base[
                base["base_id"]
            ]
        )

        if observed != expected_conditions:
            errors.append(
                base["base_id"]
                + ": incomplete "
                "condition set"
            )

    doc_counts = defaultdict(list)
    partial_ratios = []
    cue_hits = 0

    for x in instances:

        docs = x["evidence_docs"]

        doc_counts[
            x["condition"]
        ].append(len(docs))

        if not docs:
            errors.append(
                x["instance_id"]
                + ": zero documents"
            )
            continue

        doc_ids = [
            d["doc_id"]
            for d in docs
        ]

        if len(doc_ids) != len(
            set(doc_ids)
        ):
            errors.append(
                x["instance_id"]
                + ": duplicate doc IDs"
            )

        if any(
            not norm(d["text"])
            for d in docs
        ):
            errors.append(
                x["instance_id"]
                + ": empty evidence"
            )

        gold_ids = set(
            x["gold_doc_ids"]
        )

        present = set(
            doc_ids
        )

        roles = [
            d["evidence_role"]
            for d in docs
        ]

        condition = x["condition"]

        if condition == "clean":

            if not gold_ids.issubset(
                present
            ):
                errors.append(
                    x["instance_id"]
                    + ": clean lost "
                    "gold evidence"
                )

            if any(
                r != "support"
                for r in roles
            ):
                errors.append(
                    x["instance_id"]
                    + ": clean has "
                    "non-support doc"
                )

        elif condition == "missing":

            if gold_ids & present:
                errors.append(
                    x["instance_id"]
                    + ": missing has "
                    "gold evidence"
                )

            if "support" in roles:
                errors.append(
                    x["instance_id"]
                    + ": missing has "
                    "support role"
                )

        elif condition == "partial":

            if gold_ids & present:
                errors.append(
                    x["instance_id"]
                    + ": partial uses "
                    "original gold ID"
                )

            if (
                "partial_support"
                not in roles
            ):
                errors.append(
                    x["instance_id"]
                    + ": no partial "
                    "support doc"
                )

            ratio = float(
                x["metadata"].get(
                    "partial_retained_ratio",
                    -1,
                )
            )

            partial_ratios.append(
                ratio
            )

            if not (
                0.0 < ratio <= 0.80
            ):
                errors.append(
                    x["instance_id"]
                    + ": invalid "
                    f"partial ratio "
                    f"{ratio:.3f}"
                )

            # Independent partial-answer leakage gate.
            if answer_family(
                x["gold_answer"]
            ) not in {
                "ynm",
                "fever_label",
            }:
                leaked_docs = [
                    d["doc_id"]
                    for d in docs
                    if answer_leak(
                        d["text"],
                        x["gold_answer"],
                    )
                ]

                if leaked_docs:
                    errors.append(
                        x["instance_id"]
                        + ": partial exposes "
                        "gold answer in "
                        + str(leaked_docs)
                    )

        elif condition == "noisy":

            if not gold_ids.issubset(
                present
            ):
                errors.append(
                    x["instance_id"]
                    + ": noisy lost "
                    "gold evidence"
                )

            if (
                "semantic_distractor"
                not in roles
            ):
                errors.append(
                    x["instance_id"]
                    + ": noisy lacks "
                    "distractor"
                )

        elif condition == (
            "contradictory"
        ):

            if not gold_ids.issubset(
                present
            ):
                errors.append(
                    x["instance_id"]
                    + ": contradiction "
                    "lost gold"
                )

            if roles.count(
                "contradictory"
            ) != 1:
                errors.append(
                    x["instance_id"]
                    + ": contradiction "
                    "doc count != 1"
                )

        elif condition == "stale":

            if gold_ids & present:
                errors.append(
                    x["instance_id"]
                    + ": stale contains "
                    "current gold"
                )

            if roles.count(
                "stale"
            ) != 1:
                errors.append(
                    x["instance_id"]
                    + ": stale doc "
                    "count != 1"
                )

            year = x[
                "metadata"
            ].get(
                "snapshot_year"
            )

            if not (
                isinstance(year, int)
                and year < 2026
            ):
                errors.append(
                    x["instance_id"]
                    + ": invalid "
                    "snapshot year"
                )

        if condition in {
            "contradictory",
            "stale",
        }:

            for d in docs:

                if d[
                    "evidence_role"
                ] not in {
                    "contradictory",
                    "stale",
                }:
                    continue

                text = (
                    d["title"]
                    + " "
                    + d["text"]
                ).lower()

                hits = [
                    term
                    for term in
                    FORBIDDEN_SYNTHETIC_CUES
                    if term in text
                ]

                if hits:
                    cue_hits += 1

                    errors.append(
                        x["instance_id"]
                        + ": explicit cue "
                        + str(hits)
                    )

    summary = {
        "total_base_items":
            len(base_items),

        "total_instances":
            len(instances),

        "condition_counts":
            dict(
                sorted(
                    counts.items()
                )
            ),

        "doc_counts": {
            c: {
                "min": min(v),
                "mean":
                    float(np.mean(v)),
                "max": max(v),
            }
            for c, v in
            sorted(
                doc_counts.items()
            )
        },

        "partial_retained_ratio": {
            "min":
                float(
                    np.min(
                        partial_ratios
                    )
                ),
            "mean":
                float(
                    np.mean(
                        partial_ratios
                    )
                ),
            "median":
                float(
                    np.median(
                        partial_ratios
                    )
                ),
            "max":
                float(
                    np.max(
                        partial_ratios
                    )
                ),
        },

        "synthetic_cue_hits":
            cue_hits,

        "error_count":
            len(errors),
    }

    return summary, errors


def manual_sample(
    instances,
    path,
):
    groups = defaultdict(list)

    for x in instances:
        groups[
            (
                x["dataset"],
                x["condition"],
            )
        ].append(x)

    selected = []

    for key in sorted(groups):

        rows = groups[key]

        selected.append(
            rng_for(
                key[0],
                key[1],
                "manual",
            ).choice(rows)
        )

    write_jsonl(
        path,
        selected,
    )


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--base_items",
        default=(
            "revision_v3/data/"
            "base_items_v3_2k.jsonl"
        ),
    )

    parser.add_argument(
        "--out",
        default=(
            "revision_v3/data/"
            "dangermap_instances_v3_"
            "12k.jsonl"
        ),
    )

    parser.add_argument(
        "--semantic_cache",
        default=(
            "revision_v3/phase1b/"
            "semantic_distractors_"
            "v3.json"
        ),
    )

    parser.add_argument(
        "--manifest",
        default=(
            "revision_v3/phase1b/"
            "perturbation_v3_"
            "manifest.json"
        ),
    )

    parser.add_argument(
        "--quality_report",
        default=(
            "revision_v3/phase1b/"
            "perturbation_v3_"
            "quality.json"
        ),
    )

    parser.add_argument(
        "--manual_samples",
        default=(
            "revision_v3/phase1b/"
            "perturbation_v3_"
            "manual_samples.jsonl"
        ),
    )

    parser.add_argument(
        "--batch_size",
        type=int,
        default=128,
    )

    parser.add_argument(
        "--top_k_noise",
        type=int,
        default=8,
    )

    parser.add_argument(
        "--max_docs",
        type=int,
        default=12,
    )

    parser.add_argument(
        "--max_chars_per_doc",
        type=int,
        default=3000,
    )

    parser.add_argument(
        "--device",
        default="cuda",
    )

    args = parser.parse_args()

    if (
        args.device == "cuda"
        and not torch.cuda.is_available()
    ):
        raise RuntimeError(
            "CUDA unavailable"
        )

    random.seed(SEED)
    np.random.seed(SEED)
    torch.manual_seed(SEED)

    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(
            SEED
        )

    print("=" * 80)
    print(
        "DANGERMAP-RAG PHASE 1B-2: "
        "CORRECTED V3 PERTURBATIONS"
    )
    print("=" * 80)

    base_items = read_jsonl(
        args.base_items
    )

    print(
        "Base items:",
        len(base_items),
    )

    print(
        "Base SHA256:",
        sha256(args.base_items),
    )

    max_gold_docs = max(
        len(
            x.get(
                "gold_evidence",
                [],
            )
        )
        for x in base_items
    )

    print(
        "Maximum gold docs:",
        max_gold_docs,
    )

    if max_gold_docs > args.max_docs:
        raise RuntimeError(
            f"max_docs={args.max_docs} "
            "would truncate clean "
            f"gold evidence; max is "
            f"{max_gold_docs}"
        )

    base_sha = sha256(
        args.base_items
    )

    cache_path = Path(
        args.semantic_cache
    )

    semantic_noise = None

    if cache_path.exists():

        cached = json.loads(
            cache_path.read_text(
                encoding="utf-8"
            )
        )

        valid = (
            cached.get(
                "base_sha256"
            ) == base_sha
            and cached.get(
                "model"
            ) == BGE_MODEL
            and cached.get(
                "revision"
            ) == BGE_REVISION
            and cached.get(
                "top_k"
            ) == args.top_k_noise
            and cached.get(
                "max_chars"
            ) == args.max_chars_per_doc
        )

        if valid:
            semantic_noise = (
                cached[
                    "distractors"
                ]
            )

            print(
                "Loaded verified "
                "semantic cache."
            )

    if semantic_noise is None:

        pool = doc_pool(
            base_items,
            args.max_chars_per_doc,
        )

        print(
            "Document pool:",
            len(pool),
        )

        print(
            "Loading pinned BGE..."
        )

        model = SentenceTransformer(
            BGE_MODEL,
            revision=BGE_REVISION,
            device=args.device,
        )

        semantic_noise = (
            semantic_distractors(
                base_items,
                pool,
                model,
                args.batch_size,
                args.top_k_noise,
            )
        )

        cache_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        cache_path.write_text(
            json.dumps(
                {
                    "base_sha256":
                        base_sha,
                    "model":
                        BGE_MODEL,
                    "revision":
                        BGE_REVISION,
                    "top_k":
                        args.top_k_noise,
                    "max_chars":
                        args.max_chars_per_doc,
                    "distractors":
                        semantic_noise,
                },
                indent=2,
            ),
            encoding="utf-8",
        )

        print(
            "Saved semantic cache:",
            cache_path,
        )

    pools = answer_pools(
        base_items
    )

    instances = build_instances(
        base_items,
        semantic_noise,
        pools,
        args.max_docs,
        args.max_chars_per_doc,
    )

    summary, errors = audit(
        base_items,
        instances,
    )

    Path(
        args.quality_report
    ).write_text(
        json.dumps(
            {
                "summary": summary,
                "errors": errors,
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    print()
    print(
        "Quality summary:"
    )

    print(
        json.dumps(
            summary,
            indent=2,
        )
    )

    if errors:

        print()
        print(
            "PHASE 1B-2 "
            "QUALITY GATE: FAILED"
        )

        for e in errors[:100]:
            print(" -", e)

        raise SystemExit(1)

    write_jsonl(
        args.out,
        instances,
    )

    manual_sample(
        instances,
        args.manual_samples,
    )

    manifest = {
        "benchmark_version":
            "revision_v3",

        "random_seed":
            SEED,

        "base_items":
            args.base_items,

        "base_sha256":
            base_sha,

        "instances":
            args.out,

        "instances_sha256":
            sha256(args.out),

        "total_instances":
            len(instances),

        "conditions":
            CONDITIONS,

        "embedding_model":
            BGE_MODEL,

        "embedding_revision":
            BGE_REVISION,

        "top_k_noise":
            args.top_k_noise,

        "max_docs":
            args.max_docs,

        "max_chars_per_doc":
            args.max_chars_per_doc,

        "condition_definitions": {
            "clean":
                "Gold supporting "
                "evidence only.",

            "missing":
                "All gold evidence "
                "removed; semantic "
                "non-gold retrievals "
                "only.",

            "partial":
                "Original support "
                "reduced by decisive-"
                "region removal.",

            "noisy":
                "Gold support "
                "preserved and mixed "
                "with semantic "
                "distractors.",

            "contradictory":
                "Gold support plus "
                "one neutral record "
                "asserting an "
                "alternative answer.",

            "stale":
                "Current gold support "
                "removed; an archived "
                "dated snapshot asserts "
                "an alternative answer.",
        },

        "quality":
            summary,
    }

    Path(
        args.manifest
    ).write_text(
        json.dumps(
            manifest,
            indent=2,
        ),
        encoding="utf-8",
    )

    print()
    print(
        "Output:",
        args.out,
    )

    print(
        "SHA256:",
        manifest[
            "instances_sha256"
        ],
    )

    print(
        "Manual audit sample:",
        args.manual_samples,
    )

    print("=" * 80)
    print(
        "PHASE 1B-2: PASSED"
    )
    print("=" * 80)


if __name__ == "__main__":
    main()
