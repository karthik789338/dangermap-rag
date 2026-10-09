import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(
    0,
    "revision_v3/phase4/scripts",
)

from score_correctness_v3 import (
    numeric_mentions,
    mentions_equivalent,
    _equivalent_numeric_groups,
    _explicit_numeric_answer_segment,
)


ROOT = Path(
    "revision_v3/phase4/data"
)

OUT = Path(
    "revision_v3/phase4/results/"
    "numeric_candidate_rules_audit_v3.json"
)

SAMPLES_OUT = Path(
    "revision_v3/phase4/results/"
    "numeric_candidate_rules_samples_v3.jsonl"
)


MODELS = [
    "qwen25_3b",
    "qwen25_7b",
    "mistral_7b",
    "phi35_mini",
    "granite33_8b",
    "falcon3_7b",
]


def matches_gold(
    mention,
    gold_mentions,
):
    return any(
        mentions_equivalent(
            mention,
            gold,
        )
        for gold in gold_mentions
    )


def mention_equivalent_to_any(
    mention,
    others,
):
    return any(
        mentions_equivalent(
            mention,
            other,
        )
        for other in others
    )


print("=" * 120)
print(
    "DANGERMAP-RAG PHASE 4C-4: "
    "NUMERIC CANDIDATE-RULE AUDIT"
)
print("=" * 120)


report = {
    "models": {}
}

sample_rows = []

grand = Counter()


for model in MODELS:

    p = (
        ROOT
        / f"{model}_correctness_final_v3.jsonl"
    )

    c = Counter()

    model_samples = []

    with p.open(
        "r",
        encoding="utf-8",
    ) as f:

        for line in f:

            if not line.strip():
                continue

            x = json.loads(line)

            if (
                x.get(
                    "correctness_method"
                )
                != "numeric_ambiguous"
            ):
                continue

            c["total"] += 1

            answer = str(
                x.get(
                    "answer_text",
                    ""
                )
            )

            question = str(
                x.get(
                    "question",
                    ""
                )
            )

            gold = str(
                x.get(
                    "gold_answer",
                    ""
                )
            )

            answer_mentions = (
                numeric_mentions(
                    answer
                )
            )

            question_mentions = (
                numeric_mentions(
                    question
                )
            )

            gold_mentions = (
                numeric_mentions(
                    gold
                )
            )

            if not (
                answer_mentions
                and gold_mentions
            ):
                c[
                    "unexpected_missing_mentions"
                ] += 1
                continue

            # --------------------------------------------------
            # First / last number behavior.
            # Diagnostic only.
            # --------------------------------------------------
            first_match = matches_gold(
                answer_mentions[0],
                gold_mentions,
            )

            last_match = matches_gold(
                answer_mentions[-1],
                gold_mentions,
            )

            if first_match:
                c[
                    "first_number_matches_gold"
                ] += 1

            if last_match:
                c[
                    "last_number_matches_gold"
                ] += 1

            if (
                first_match
                and last_match
            ):
                c[
                    "first_and_last_match"
                ] += 1

            # --------------------------------------------------
            # Remove numbers repeated directly from the question,
            # unless that value itself is the gold answer.
            # This tests whether contextual years / quantities
            # explain much of the ambiguity.
            # --------------------------------------------------
            filtered = []

            for mention in answer_mentions:

                is_gold = matches_gold(
                    mention,
                    gold_mentions,
                )

                appears_in_question = (
                    mention_equivalent_to_any(
                        mention,
                        question_mentions,
                    )
                )

                if (
                    appears_in_question
                    and not is_gold
                ):
                    continue

                filtered.append(
                    mention
                )

            filtered_groups = (
                _equivalent_numeric_groups(
                    filtered
                )
                if filtered
                else []
            )

            if len(
                filtered_groups
            ) == 1:

                c[
                    "unique_after_question_filter"
                ] += 1

                candidate = (
                    filtered_groups[0][0]
                )

                if matches_gold(
                    candidate,
                    gold_mentions,
                ):
                    c[
                        "unique_after_question_filter_matches_gold"
                    ] += 1

            # --------------------------------------------------
            # Last '=' RHS.
            # A mathematically interpretable extraction rule.
            # --------------------------------------------------
            if "=" in answer:

                rhs = answer.rsplit(
                    "=",
                    1,
                )[1]

                rhs_mentions = (
                    numeric_mentions(
                        rhs
                    )
                )

                rhs_groups = (
                    _equivalent_numeric_groups(
                        rhs_mentions
                    )
                    if rhs_mentions
                    else []
                )

                if len(
                    rhs_groups
                ) == 1:

                    c[
                        "unique_last_equation_rhs"
                    ] += 1

                    candidate = (
                        rhs_groups[0][0]
                    )

                    if matches_gold(
                        candidate,
                        gold_mentions,
                    ):
                        c[
                            "unique_last_equation_rhs_matches_gold"
                        ] += 1

            # --------------------------------------------------
            # Explicit-answer segment.
            # Current conservative rule already tries this.
            # --------------------------------------------------
            explicit = (
                _explicit_numeric_answer_segment(
                    answer
                )
            )

            if explicit:

                explicit_mentions = (
                    numeric_mentions(
                        explicit
                    )
                )

                explicit_groups = (
                    _equivalent_numeric_groups(
                        explicit_mentions
                    )
                    if explicit_mentions
                    else []
                )

                if len(
                    explicit_groups
                ) == 1:

                    c[
                        "unique_explicit_candidate"
                    ] += 1

                    candidate = (
                        explicit_groups[0][0]
                    )

                    if matches_gold(
                        candidate,
                        gold_mentions,
                    ):
                        c[
                            "unique_explicit_candidate_matches_gold"
                        ] += 1

            # --------------------------------------------------
            # Small stratified qualitative packet.
            # Two examples/model where possible.
            # --------------------------------------------------
            if len(
                model_samples
            ) < 2:

                model_samples.append({
                    "model":
                        model,

                    "instance_id":
                        x["instance_id"],

                    "dataset":
                        x["dataset"],

                    "condition":
                        x["condition"],

                    "question":
                        question,

                    "gold_answer":
                        gold,

                    "answer_text":
                        answer,

                    "answer_numeric_mentions":
                        answer_mentions,

                    "question_numeric_mentions":
                        question_mentions,

                    "last_number_matches_gold":
                        first_match
                        if len(
                            answer_mentions
                        ) == 1
                        else last_match,

                    "filtered_numeric_mentions":
                        filtered,

                    "explicit_answer_segment":
                        explicit,
                })

    sample_rows.extend(
        model_samples
    )

    report[
        "models"
    ][model] = dict(
        c
    )

    grand.update(c)

    def pct(
        numerator,
        denominator,
    ):
        if not denominator:
            return 0.0

        return (
            100.0
            * numerator
            / denominator
        )

    print(
        f"{model:16s} "
        f"n={c['total']:4d}  "
        f"last_match="
        f"{c['last_number_matches_gold']:4d} "
        f"({pct(c['last_number_matches_gold'], c['total']):5.1f}%)  "
        f"qfilter_unique="
        f"{c['unique_after_question_filter']:4d}  "
        f"qfilter_correct="
        f"{c['unique_after_question_filter_matches_gold']:4d}  "
        f"eq_rhs="
        f"{c['unique_last_equation_rhs']:4d}"
    )


report[
    "overall"
] = dict(
    grand
)


OUT.write_text(
    json.dumps(
        report,
        indent=2,
    ),
    encoding="utf-8",
)


with SAMPLES_OUT.open(
    "w",
    encoding="utf-8",
) as f:

    for row in sample_rows:

        f.write(
            json.dumps(
                row,
                ensure_ascii=False,
            )
            + "\n"
        )


print("-" * 120)

print(
    f"{'TOTAL':16s} "
    f"n={grand['total']:5d}  "
    f"last_match="
    f"{grand['last_number_matches_gold']:5d}  "
    f"qfilter_unique="
    f"{grand['unique_after_question_filter']:5d}  "
    f"qfilter_correct="
    f"{grand['unique_after_question_filter_matches_gold']:5d}  "
    f"eq_rhs="
    f"{grand['unique_last_equation_rhs']:5d}  "
    f"eq_rhs_correct="
    f"{grand['unique_last_equation_rhs_matches_gold']:5d}"
)

print("=" * 120)

print(
    "Audit:",
    OUT,
)

print(
    "Samples:",
    SAMPLES_OUT,
)

print(
    "PHASE 4C-4 NUMERIC RULE AUDIT: COMPLETE"
)

print("=" * 120)
