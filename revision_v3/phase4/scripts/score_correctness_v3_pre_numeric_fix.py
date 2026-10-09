import json
import math
import re
import string
from collections import Counter
from pathlib import Path


INPUT_ROOT = Path(
    "revision_v3/phase4/data"
)

OUT_ROOT = Path(
    "revision_v3/phase4/data"
)

SUMMARY_PATH = Path(
    "revision_v3/phase4/results/"
    "correctness_summary_v3.json"
)


MODELS = [
    "qwen25_3b",
    "qwen25_7b",
    "mistral_7b",
    "phi35_mini",
    "granite33_8b",
    "falcon3_7b",
]


ARTICLES = {
    "a",
    "an",
    "the",
}


# ------------------------------------------------------------------
# Text scoring
# ------------------------------------------------------------------

def normalize_text(value):

    if value is None:
        return ""

    text = str(value).lower()

    text = text.translate(
        str.maketrans(
            "",
            "",
            string.punctuation,
        )
    )

    tokens = [
        token
        for token in text.split()
        if token not in ARTICLES
    ]

    return " ".join(tokens)


def exact_match(
    prediction,
    gold,
):
    return float(
        normalize_text(prediction)
        == normalize_text(gold)
    )


def token_f1(
    prediction,
    gold,
):
    pred_tokens = (
        normalize_text(
            prediction
        ).split()
    )

    gold_tokens = (
        normalize_text(
            gold
        ).split()
    )

    if (
        not pred_tokens
        and not gold_tokens
    ):
        return 1.0

    if (
        not pred_tokens
        or not gold_tokens
    ):
        return 0.0

    pred_counts = Counter(
        pred_tokens
    )

    gold_counts = Counter(
        gold_tokens
    )

    common = (
        pred_counts
        & gold_counts
    )

    overlap = sum(
        common.values()
    )

    if overlap == 0:
        return 0.0

    precision = (
        overlap
        / len(pred_tokens)
    )

    recall = (
        overlap
        / len(gold_tokens)
    )

    return (
        2
        * precision
        * recall
        / (
            precision
            + recall
        )
    )


def strip_option_prefix(text):

    if text is None:
        return text

    text = str(text).strip()

    return re.sub(
        r"^\s*[\(\[]?"
        r"[A-Ea-e]"
        r"[\)\]\.\:\-]?\s+",
        "",
        text,
        count=1,
    )


# ------------------------------------------------------------------
# Classification tasks
# ------------------------------------------------------------------

def first_meaningful_phrase(text):

    text = str(text).strip().lower()

    text = re.sub(
        r"^[\s\"'`*_#]+",
        "",
        text,
    )

    return text


def classify_fever(text):

    if text is None:
        return None

    t = first_meaningful_phrase(
        text
    )

    # Direct dataset labels.
    if re.match(
        r"^supports?\b",
        t,
    ):
        return "SUPPORTS"

    if re.match(
        r"^refutes?\b",
        t,
    ):
        return "REFUTES"

    # Common direct equivalents.
    if re.match(
        r"^(true|yes)\b",
        t,
    ):
        return "SUPPORTS"

    if re.match(
        r"^(false|no)\b",
        t,
    ):
        return "REFUTES"

    patterns_support = [
        r"^the claim is supported\b",
        r"^the evidence supports\b",
        r"^the claim is true\b",
        r"^the claim is correct\b",
    ]

    patterns_refute = [
        r"^the claim is refuted\b",
        r"^the evidence refutes\b",
        r"^the claim is false\b",
        r"^the claim is incorrect\b",
    ]

    if any(
        re.match(p, t)
        for p in patterns_support
    ):
        return "SUPPORTS"

    if any(
        re.match(p, t)
        for p in patterns_refute
    ):
        return "REFUTES"

    return None


def classify_pubmedqa(text):

    if text is None:
        return None

    t = first_meaningful_phrase(
        text
    )

    if re.match(
        r"^yes\b",
        t,
    ):
        return "yes"

    if re.match(
        r"^no\b",
        t,
    ):
        return "no"

    if re.match(
        r"^maybe\b",
        t,
    ):
        return "maybe"

    if re.match(
        r"^(uncertain|inconclusive)\b",
        t,
    ):
        return "maybe"

    return None


# ------------------------------------------------------------------
# Numeric tasks
# ------------------------------------------------------------------

NUMBER_RE = re.compile(
    r"""
    (?<![\w])
    [-+]?
    (?:
        (?:\d{1,3}(?:,\d{3})+)
        |
        (?:\d+)
    )
    (?:\.\d+)?
    \s*%?
    """,
    flags=re.VERBOSE,
)


def numeric_mentions(text):

    if text is None:
        return []

    text = str(text)

    mentions = []

    for match in NUMBER_RE.finditer(
        text
    ):

        raw = match.group(
            0
        ).strip()

        is_percent = (
            raw.endswith("%")
        )

        cleaned = (
            raw
            .replace(",", "")
            .replace("%", "")
            .strip()
        )

        try:
            value = float(
                cleaned
            )

        except ValueError:
            continue

        if not math.isfinite(
            value
        ):
            continue

        mentions.append({
            "raw":
                raw,

            "value":
                value,

            "percent":
                is_percent,
        })

    return mentions


def close_numeric(
    a,
    b,
):
    return math.isclose(
        float(a),
        float(b),
        rel_tol=1e-4,
        abs_tol=1e-4,
    )


def mentions_equivalent(
    pred,
    gold,
):

    p = pred["value"]
    g = gold["value"]

    if close_numeric(
        p,
        g,
    ):
        return True

    # Percentage-format equivalence:
    # 25% <-> 0.25
    if (
        pred["percent"]
        and not gold["percent"]
    ):
        if close_numeric(
            p / 100.0,
            g,
        ):
            return True

    if (
        gold["percent"]
        and not pred["percent"]
    ):
        if close_numeric(
            p,
            g / 100.0,
        ):
            return True

    return False


def numeric_gold_detected(
    gold,
):
    mentions = (
        numeric_mentions(
            gold
        )
    )

    # Treat the gold as numeric only when
    # there is at least one numeric value
    # and little substantive nonnumeric text.
    if not mentions:
        return False

    residual = NUMBER_RE.sub(
        " ",
        str(gold),
    )

    residual = re.sub(
        r"[$€£¥(),:\s\-]+",
        " ",
        residual,
    )

    residual = residual.strip()

    # Units are allowed.
    allowed_units = {
        "",
        "million",
        "millions",
        "billion",
        "billions",
        "thousand",
        "thousands",
        "percent",
        "percentage",
        "dollars",
        "dollar",
        "years",
        "year",
        "months",
        "month",
        "days",
        "day",
    }

    return (
        residual.lower()
        in allowed_units
    )


def numeric_match(
    prediction,
    gold,
):
    pred_mentions = (
        numeric_mentions(
            prediction
        )
    )

    gold_mentions = (
        numeric_mentions(
            gold
        )
    )

    if not gold_mentions:
        return None

    if not pred_mentions:
        return 0.0

    for p in pred_mentions:
        for g in gold_mentions:

            if mentions_equivalent(
                p,
                g,
            ):
                return 1.0

    return 0.0


# ------------------------------------------------------------------
# Dataset-aware scoring
# ------------------------------------------------------------------

def score_correctness(
    dataset,
    prediction,
    gold,
):

    if prediction is None:
        return {
            "automated_correctness":
                None,

            "correctness_method":
                "unavailable",

            "exact_match":
                None,

            "token_f1":
                None,

            "predicted_label":
                None,

            "gold_label":
                None,

            "numeric_match":
                None,
        }


    if dataset == "fever":

        predicted = (
            classify_fever(
                prediction
            )
        )

        gold_label = (
            str(gold)
            .strip()
            .upper()
        )

        if predicted is None:

            score = None
            method = (
                "fever_unmapped_"
                "pending_semantic"
            )

        else:

            score = float(
                predicted
                == gold_label
            )

            method = (
                "fever_label"
            )

        return {
            "automated_correctness":
                score,

            "correctness_method":
                method,

            "exact_match":
                None,

            "token_f1":
                None,

            "predicted_label":
                predicted,

            "gold_label":
                gold_label,

            "numeric_match":
                None,
        }


    if dataset == "pubmedqa":

        predicted = (
            classify_pubmedqa(
                prediction
            )
        )

        gold_label = (
            str(gold)
            .strip()
            .lower()
        )

        if predicted is None:

            score = None
            method = (
                "pubmedqa_unmapped_"
                "pending_semantic"
            )

        else:

            score = float(
                predicted
                == gold_label
            )

            method = (
                "pubmedqa_label"
            )

        return {
            "automated_correctness":
                score,

            "correctness_method":
                method,

            "exact_match":
                None,

            "token_f1":
                None,

            "predicted_label":
                predicted,

            "gold_label":
                gold_label,

            "numeric_match":
                None,
        }


    if dataset in {
        "finqa",
        "tatqa",
    }:

        if numeric_gold_detected(
            gold
        ):

            nm = numeric_match(
                prediction,
                gold,
            )

            return {
                "automated_correctness":
                    nm,

                "correctness_method":
                    "numeric_equivalence",

                "exact_match":
                    exact_match(
                        prediction,
                        gold,
                    ),

                "token_f1":
                    token_f1(
                        prediction,
                        gold,
                    ),

                "predicted_label":
                    None,

                "gold_label":
                    None,

                "numeric_match":
                    nm,
            }

        em = exact_match(
            prediction,
            gold,
        )

        f1 = token_f1(
            prediction,
            gold,
        )

        return {
            "automated_correctness":
                f1,

            "correctness_method":
                "normalized_token_f1",

            "exact_match":
                em,

            "token_f1":
                f1,

            "predicted_label":
                None,

            "gold_label":
                None,

            "numeric_match":
                None,
        }


    if dataset == "casehold":

        pred = strip_option_prefix(
            prediction
        )

        gold_clean = (
            strip_option_prefix(
                gold
            )
        )

        em = exact_match(
            pred,
            gold_clean,
        )

        f1 = token_f1(
            pred,
            gold_clean,
        )

        return {
            "automated_correctness":
                f1,

            "correctness_method":
                "casehold_token_f1",

            "exact_match":
                em,

            "token_f1":
                f1,

            "predicted_label":
                None,

            "gold_label":
                None,

            "numeric_match":
                None,
        }


    # HotpotQA and CUAD.
    if dataset in {
        "hotpotqa",
        "cuad",
    }:

        em = exact_match(
            prediction,
            gold,
        )

        f1 = token_f1(
            prediction,
            gold,
        )

        return {
            "automated_correctness":
                f1,

            "correctness_method":
                "normalized_token_f1",

            "exact_match":
                em,

            "token_f1":
                f1,

            "predicted_label":
                None,

            "gold_label":
                None,

            "numeric_match":
                None,
        }


    raise ValueError(
        "Unknown dataset: "
        + str(dataset)
    )


# ------------------------------------------------------------------
# Full corpus
# ------------------------------------------------------------------

def main():

    OUT_ROOT.mkdir(
        parents=True,
        exist_ok=True,
    )

    summary = {
        "models": {},
    }


    print("=" * 116)
    print(
        "DANGERMAP-RAG PHASE 4B: "
        "TASK-AWARE AUTOMATED CORRECTNESS"
    )
    print("=" * 116)


    for model in MODELS:

        inp = (
            INPUT_ROOT
            / f"{model}_analysis_ready_v3.jsonl"
        )

        out = (
            OUT_ROOT
            / f"{model}_scored_correctness_v3.jsonl"
        )

        counts = Counter()

        dataset_stats = {}

        with inp.open(
            "r",
            encoding="utf-8",
        ) as fin, out.open(
            "w",
            encoding="utf-8",
        ) as fout:

            for line in fin:

                if not line.strip():
                    continue

                row = json.loads(
                    line
                )

                counts["total"] += 1

                result = (
                    score_correctness(
                        dataset=row[
                            "dataset"
                        ],

                        prediction=row[
                            "answer_text"
                        ],

                        gold=row[
                            "gold_answer"
                        ],
                    )
                )

                row.update(
                    result
                )

                score = result[
                    "automated_correctness"
                ]

                dataset = row[
                    "dataset"
                ]

                if dataset not in dataset_stats:
                    dataset_stats[
                        dataset
                    ] = Counter()

                ds = dataset_stats[
                    dataset
                ]

                ds["total"] += 1

                if score is None:

                    counts[
                        "correctness_missing"
                    ] += 1

                    ds[
                        "correctness_missing"
                    ] += 1

                else:

                    if not (
                        0.0
                        <= float(score)
                        <= 1.0
                    ):
                        raise RuntimeError(
                            f"Out-of-range "
                            f"correctness: {score}"
                        )

                    counts[
                        "correctness_available"
                    ] += 1

                    ds[
                        "correctness_available"
                    ] += 1

                    ds[
                        "score_sum"
                    ] += float(
                        score
                    )

                    if (
                        float(score)
                        >= 0.50
                    ):
                        counts[
                            "correct_at_reference"
                        ] += 1

                        ds[
                            "correct_at_reference"
                        ] += 1

                method = result[
                    "correctness_method"
                ]

                counts[
                    "method::" + method
                ] += 1

                ds[
                    "method::" + method
                ] += 1

                fout.write(
                    json.dumps(
                        row,
                        ensure_ascii=False,
                    )
                    + "\n"
                )


        model_dataset_summary = {}

        for dataset, ds in sorted(
            dataset_stats.items()
        ):

            available = ds[
                "correctness_available"
            ]

            model_dataset_summary[
                dataset
            ] = {
                "total":
                    ds["total"],

                "correctness_available":
                    available,

                "correctness_missing":
                    ds[
                        "correctness_missing"
                    ],

                "mean_automated_correctness":
                    (
                        ds["score_sum"]
                        / available
                        if available
                        else None
                    ),

                "fraction_ge_0p50":
                    (
                        ds[
                            "correct_at_reference"
                        ]
                        / available
                        if available
                        else None
                    ),

                "methods": {
                    key.split(
                        "::",
                        1,
                    )[1]:
                        value

                    for key, value
                    in sorted(
                        ds.items()
                    )

                    if key.startswith(
                        "method::"
                    )
                },
            }


        summary[
            "models"
        ][model] = {
            "counts":
                dict(counts),

            "datasets":
                model_dataset_summary,
        }


        print(
            f"{model:16s} "
            f"available="
            f"{counts['correctness_available']:5d} "
            f"missing="
            f"{counts['correctness_missing']:4d} "
            f">=0.5="
            f"{counts['correct_at_reference']:5d}"
        )


    SUMMARY_PATH.write_text(
        json.dumps(
            summary,
            indent=2,
        ),
        encoding="utf-8",
    )


    print("=" * 116)
    print(
        "Summary:",
        SUMMARY_PATH,
    )
    print(
        "PHASE 4B CORRECTNESS SCORING: COMPLETE"
    )
    print("=" * 116)


if __name__ == "__main__":
    main()
