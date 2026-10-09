import json
import re
from collections import Counter
from pathlib import Path

import torch
from transformers import (
    AutoModelForSequenceClassification,
    AutoTokenizer,
)


INPUT_ROOT = Path(
    "revision_v3/phase4/data"
)

OUTPUT_ROOT = Path(
    "revision_v3/phase4/data"
)

SUMMARY_PATH = Path(
    "revision_v3/phase4/results/"
    "semantic_correctness_fallback_summary_v3.json"
)


MODEL_ID = (
    "MoritzLaurer/"
    "DeBERTa-v3-base-mnli-fever-anli"
)

REVISION = (
    "6f5cf0a2b59cabb106aca4c287eed12e357e90eb"
)


MODELS = [
    "qwen25_3b",
    "qwen25_7b",
    "mistral_7b",
    "phi35_mini",
    "granite33_8b",
    "falcon3_7b",
]


DEVICE = (
    "cuda"
    if torch.cuda.is_available()
    else "cpu"
)

BATCH_SIZE = 64
MAX_LENGTH = 512


tokenizer = (
    AutoTokenizer
    .from_pretrained(
        MODEL_ID,
        revision=REVISION,
    )
)

model = (
    AutoModelForSequenceClassification
    .from_pretrained(
        MODEL_ID,
        revision=REVISION,
        dtype=(
            torch.float16
            if DEVICE == "cuda"
            else torch.float32
        ),
    )
    .to(DEVICE)
)

model.eval()


id2label = {
    int(k): str(v).lower()
    for k, v in
    model.config.id2label.items()
}


def find_label_id(fragment):

    matches = [
        idx
        for idx, label
        in id2label.items()
        if fragment in label
    ]

    if len(matches) != 1:
        raise RuntimeError(
            f"Could not uniquely identify "
            f"{fragment!r} label from "
            f"{id2label}"
        )

    return matches[0]


ENTAIL_ID = find_label_id(
    "entail"
)

CONTRA_ID = find_label_id(
    "contrad"
)

NEUTRAL_ID = find_label_id(
    "neutral"
)


print("=" * 108)
print(
    "DANGERMAP-RAG PHASE 4C-2: "
    "SEMANTIC CORRECTNESS FALLBACK"
)
print("=" * 108)

print(
    "Model:",
    MODEL_ID,
)

print(
    "Revision:",
    REVISION,
)

print(
    "Device:",
    DEVICE,
)

print(
    "id2label:",
    id2label,
)

print(
    "entailment ID:",
    ENTAIL_ID,
)

print(
    "contradiction ID:",
    CONTRA_ID,
)

print(
    "neutral ID:",
    NEUTRAL_ID,
)

print("=" * 108)


@torch.inference_mode()
def score_pairs(
    premises,
    hypotheses,
):

    encoded = tokenizer(
        premises,
        hypotheses,
        padding=True,
        truncation=True,
        max_length=MAX_LENGTH,
        return_tensors="pt",
    )

    encoded = {
        k: v.to(DEVICE)
        for k, v in
        encoded.items()
    }

    logits = model(
        **encoded
    ).logits

    probs = torch.softmax(
        logits.float(),
        dim=-1,
    )

    return probs.cpu()


def extract_fever_claim(
    question,
):

    text = str(
        question
    ).strip()

    return re.sub(
        r"(?i)^verify\s+this\s+claim\s*:\s*",
        "",
        text,
        count=1,
    ).strip()


def fever_fallback(
    rows,
):

    results = {}

    for start in range(
        0,
        len(rows),
        BATCH_SIZE,
    ):

        batch = rows[
            start:
            start + BATCH_SIZE
        ]

        premises = [
            x["answer_text"]
            for x in batch
        ]

        hypotheses = [
            extract_fever_claim(
                x["question"]
            )
            for x in batch
        ]

        probs = score_pairs(
            premises,
            hypotheses,
        )

        for row, p in zip(
            batch,
            probs,
        ):

            relation_id = int(
                torch.argmax(
                    p
                ).item()
            )

            if relation_id == ENTAIL_ID:
                predicted = (
                    "SUPPORTS"
                )

            elif relation_id == CONTRA_ID:
                predicted = (
                    "REFUTES"
                )

            else:
                predicted = None

            gold = str(
                row["gold_answer"]
            ).strip().upper()

            correctness = (
                float(
                    predicted == gold
                )
                if predicted is not None
                else None
            )

            results[
                row["instance_id"]
            ] = {
                "semantic_predicted_label":
                    predicted,

                "semantic_correctness":
                    correctness,

                "semantic_entailment_probability":
                    float(
                        p[
                            ENTAIL_ID
                        ].item()
                    ),

                "semantic_contradiction_probability":
                    float(
                        p[
                            CONTRA_ID
                        ].item()
                    ),

                "semantic_neutral_probability":
                    float(
                        p[
                            NEUTRAL_ID
                        ].item()
                    ),

                "semantic_method":
                    (
                        "fever_nli_relation"
                        if predicted is not None
                        else "fever_nli_neutral"
                    ),
            }

    return results


PUBMED_HYPOTHESES = {
    "yes":
        "The response gives a yes answer "
        "to the question.",

    "no":
        "The response gives a no answer "
        "to the question.",

    "maybe":
        "The response gives an uncertain "
        "or maybe answer to the question.",
}


def pubmed_fallback(
    rows,
):

    results = {}

    expanded = []

    for row in rows:

        premise = (
            "Question: "
            + str(
                row["question"]
            )
            + "\nResponse: "
            + str(
                row["answer_text"]
            )
        )

        for label, hypothesis in (
            PUBMED_HYPOTHESES.items()
        ):

            expanded.append(
                (
                    row["instance_id"],
                    label,
                    premise,
                    hypothesis,
                )
            )


    scored = {}

    for start in range(
        0,
        len(expanded),
        BATCH_SIZE,
    ):

        batch = expanded[
            start:
            start + BATCH_SIZE
        ]

        premises = [
            x[2]
            for x in batch
        ]

        hypotheses = [
            x[3]
            for x in batch
        ]

        probs = score_pairs(
            premises,
            hypotheses,
        )

        for item, p in zip(
            batch,
            probs,
        ):

            iid = item[0]
            label = item[1]

            scored.setdefault(
                iid,
                {},
            )

            scored[
                iid
            ][label] = {
                "entailment":
                    float(
                        p[
                            ENTAIL_ID
                        ].item()
                    ),

                "contradiction":
                    float(
                        p[
                            CONTRA_ID
                        ].item()
                    ),

                "neutral":
                    float(
                        p[
                            NEUTRAL_ID
                        ].item()
                    ),

                "argmax":
                    int(
                        torch.argmax(
                            p
                        ).item()
                    ),
            }


    by_id = {
        x["instance_id"]: x
        for x in rows
    }


    for iid, candidates in (
        scored.items()
    ):

        eligible = []

        for label, scores in (
            candidates.items()
        ):

            # Conservative gate:
            # that candidate's pair must itself
            # be classified as entailment.
            if (
                scores[
                    "argmax"
                ]
                == ENTAIL_ID
            ):

                eligible.append(
                    (
                        scores[
                            "entailment"
                        ],
                        label,
                    )
                )

        if eligible:

            eligible.sort(
                reverse=True
            )

            predicted = (
                eligible[0][1]
            )

        else:

            predicted = None


        gold = str(
            by_id[
                iid
            ]["gold_answer"]
        ).strip().lower()


        correctness = (
            float(
                predicted == gold
            )
            if predicted is not None
            else None
        )


        results[iid] = {
            "semantic_predicted_label":
                predicted,

            "semantic_correctness":
                correctness,

            "semantic_candidate_scores":
                candidates,

            "semantic_method":
                (
                    "pubmedqa_nli_zero_shot"
                    if predicted is not None
                    else "pubmedqa_nli_unresolved"
                ),
        }


    return results


summary = {
    "nli_model":
        MODEL_ID,

    "revision":
        REVISION,

    "models":
        {},
}


for model_name in MODELS:

    inp = (
        INPUT_ROOT
        / f"{model_name}_scored_correctness_v3.jsonl"
    )

    out = (
        OUTPUT_ROOT
        / f"{model_name}_correctness_final_v3.jsonl"
    )

    rows = [
        json.loads(x)
        for x in inp.read_text(
            encoding="utf-8"
        ).splitlines()
        if x.strip()
    ]


    fever_targets = [
        x
        for x in rows

        if (
            x["dataset"]
            == "fever"

            and x[
                "automated_correctness"
            ] is None

            and x.get(
                "answer_usable"
            )

            and x.get(
                "answer_text"
            )
        )
    ]


    pubmed_targets = [
        x
        for x in rows

        if (
            x["dataset"]
            == "pubmedqa"

            and x[
                "automated_correctness"
            ] is None

            and x.get(
                "answer_usable"
            )

            and x.get(
                "answer_text"
            )
        )
    ]


    fever_results = (
        fever_fallback(
            fever_targets
        )
    )

    pubmed_results = (
        pubmed_fallback(
            pubmed_targets
        )
    )


    semantic_results = {
        **fever_results,
        **pubmed_results,
    }


    counts = Counter()


    with out.open(
        "w",
        encoding="utf-8",
    ) as f:

        for row in rows:

            counts[
                "total"
            ] += 1

            original = row[
                "automated_correctness"
            ]

            row[
                "deterministic_correctness"
            ] = original

            row[
                "semantic_fallback_applied"
            ] = False

            row[
                "semantic_predicted_label"
            ] = None

            row[
                "semantic_correctness"
            ] = None

            row[
                "semantic_method"
            ] = None


            result = (
                semantic_results.get(
                    row[
                        "instance_id"
                    ]
                )
            )


            if result is not None:

                row[
                    "semantic_fallback_applied"
                ] = True

                for key, value in (
                    result.items()
                ):
                    row[key] = value


                if (
                    result[
                        "semantic_correctness"
                    ]
                    is not None
                ):

                    row[
                        "automated_correctness"
                    ] = result[
                        "semantic_correctness"
                    ]

                    row[
                        "correctness_method"
                    ] = result[
                        "semantic_method"
                    ]

                    counts[
                        "semantic_resolved"
                    ] += 1

                else:

                    counts[
                        "semantic_unresolved"
                    ] += 1


            if (
                row[
                    "automated_correctness"
                ]
                is None
            ):

                counts[
                    "final_missing"
                ] += 1

            else:

                counts[
                    "final_available"
                ] += 1


            f.write(
                json.dumps(
                    row,
                    ensure_ascii=False,
                )
                + "\n"
            )


    summary[
        "models"
    ][model_name] = {
        "fever_targets":
            len(
                fever_targets
            ),

        "pubmedqa_targets":
            len(
                pubmed_targets
            ),

        "semantic_resolved":
            counts[
                "semantic_resolved"
            ],

        "semantic_unresolved":
            counts[
                "semantic_unresolved"
            ],

        "final_available":
            counts[
                "final_available"
            ],

        "final_missing":
            counts[
                "final_missing"
            ],
    }


    print(
        f"{model_name:16s} "
        f"FEVER={len(fever_targets):4d} "
        f"PubMed={len(pubmed_targets):4d} "
        f"resolved="
        f"{counts['semantic_resolved']:4d} "
        f"unresolved="
        f"{counts['semantic_unresolved']:4d} "
        f"final_available="
        f"{counts['final_available']:5d} "
        f"missing="
        f"{counts['final_missing']:4d}"
    )


SUMMARY_PATH.write_text(
    json.dumps(
        summary,
        indent=2,
    ),
    encoding="utf-8",
)


print("=" * 108)
print(
    "Summary:",
    SUMMARY_PATH,
)

print(
    "PHASE 4C-2 SEMANTIC FALLBACK: COMPLETE"
)

print("=" * 108)
