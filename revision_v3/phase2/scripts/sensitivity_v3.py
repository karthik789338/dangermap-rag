import itertools
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd

from scipy.stats import spearmanr
from sklearn.metrics import cohen_kappa_score

from scoring_v3 import (
    danger_score,
    normalize_expressed_confidence,
)


REFERENCE = {
    "tau_A": 0.50,
    "tau_C": 0.70,
    "tau_V": 0.50,
}

THRESHOLD_GRID = list(
    itertools.product(
        [0.40, 0.50, 0.60],
        [0.60, 0.70, 0.80],
        [0.40, 0.50, 0.60],
    )
)

WEIGHT_REGIMES = {
    "equal": {
        "incorrectness": 0.25,
        "expressed_confidence": 0.25,
        "citation_appearance": 0.25,
        "citation_misgrounding": 0.25,
    },

    "incorrectness_heavy": {
        "incorrectness": 0.40,
        "expressed_confidence": 0.20,
        "citation_appearance": 0.20,
        "citation_misgrounding": 0.20,
    },

    "confidence_heavy": {
        "incorrectness": 0.20,
        "expressed_confidence": 0.40,
        "citation_appearance": 0.20,
        "citation_misgrounding": 0.20,
    },

    "citation_heavy": {
        "incorrectness": 0.20,
        "expressed_confidence": 0.20,
        "citation_appearance": 0.30,
        "citation_misgrounding": 0.30,
    },
}


def sf_labels(
    df,
    tau_A,
    tau_C,
    tau_V,
):
    return (
        (~df["abstained"])
        & (
            df["correctness"]
            < tau_A
        )
        & (
            df[
                "expressed_confidence"
            ]
            >= tau_C
        )
        & (
            df[
                "citation_appearance"
            ]
            >= tau_V
        )
    ).astype(int).to_numpy()


def jaccard_binary(a, b):
    a = np.asarray(
        a,
        dtype=bool,
    )

    b = np.asarray(
        b,
        dtype=bool,
    )

    union = np.logical_or(
        a,
        b,
    ).sum()

    if union == 0:
        return 1.0

    intersection = np.logical_and(
        a,
        b,
    ).sum()

    return float(
        intersection / union
    )


def safe_kappa(a, b):
    if (
        len(set(a)) == 1
        and len(set(b)) == 1
        and a[0] == b[0]
    ):
        return 1.0

    score = cohen_kappa_score(
        a,
        b,
    )

    if np.isnan(score):
        return float("nan")

    return float(score)


def clustered_rate_ci(
    df,
    labels,
    reference_labels,
    iterations=1000,
    seed=1701,
):
    """
    Cluster bootstrap at base_id.

    All rows belonging to a sampled base_id
    are sampled together.
    """

    cluster_codes, clusters = (
        pd.factorize(
            df["base_id"],
            sort=True,
        )
    )

    n_clusters = len(clusters)

    if n_clusters < 2:
        return {
            "rate_ci_low": float("nan"),
            "rate_ci_high": float("nan"),
            "delta_ci_low": float("nan"),
            "delta_ci_high": float("nan"),
        }

    rows_per_cluster = np.bincount(
        cluster_codes
    ).astype(float)

    sf_per_cluster = np.bincount(
        cluster_codes,
        weights=np.asarray(
            labels,
            dtype=float,
        ),
    )

    ref_per_cluster = np.bincount(
        cluster_codes,
        weights=np.asarray(
            reference_labels,
            dtype=float,
        ),
    )

    rng = np.random.default_rng(
        seed
    )

    rates = np.empty(
        iterations,
        dtype=float,
    )

    deltas = np.empty(
        iterations,
        dtype=float,
    )

    for i in range(iterations):
        sampled = rng.integers(
            0,
            n_clusters,
            size=n_clusters,
        )

        denominator = (
            rows_per_cluster[
                sampled
            ].sum()
        )

        rate = (
            sf_per_cluster[
                sampled
            ].sum()
            / denominator
        )

        ref_rate = (
            ref_per_cluster[
                sampled
            ].sum()
            / denominator
        )

        rates[i] = rate
        deltas[i] = (
            rate - ref_rate
        )

    return {
        "rate_ci_low":
            float(
                np.quantile(
                    rates,
                    0.025,
                )
            ),

        "rate_ci_high":
            float(
                np.quantile(
                    rates,
                    0.975,
                )
            ),

        "delta_ci_low":
            float(
                np.quantile(
                    deltas,
                    0.025,
                )
            ),

        "delta_ci_high":
            float(
                np.quantile(
                    deltas,
                    0.975,
                )
            ),
    }


def threshold_sensitivity(
    df,
    bootstrap_iterations=1000,
):
    ref = sf_labels(
        df,
        **REFERENCE,
    )

    ref_rate = float(
        np.mean(ref)
    )

    rows = []

    for (
        tau_A,
        tau_C,
        tau_V,
    ) in THRESHOLD_GRID:

        labels = sf_labels(
            df,
            tau_A,
            tau_C,
            tau_V,
        )

        rate = float(
            np.mean(labels)
        )

        row = {
            "tau_A": tau_A,
            "tau_C": tau_C,
            "tau_V": tau_V,

            "is_reference": (
                math.isclose(
                    tau_A,
                    REFERENCE["tau_A"],
                )
                and math.isclose(
                    tau_C,
                    REFERENCE["tau_C"],
                )
                and math.isclose(
                    tau_V,
                    REFERENCE["tau_V"],
                )
            ),

            "silent_failure_count":
                int(labels.sum()),

            "silent_failure_rate":
                rate,

            "reference_rate":
                ref_rate,

            "rate_change":
                rate - ref_rate,

            "absolute_rate_change":
                abs(
                    rate - ref_rate
                ),

            "jaccard_vs_reference":
                jaccard_binary(
                    labels,
                    ref,
                ),

            "kappa_vs_reference":
                safe_kappa(
                    labels.tolist(),
                    ref.tolist(),
                ),
        }

        row.update(
            clustered_rate_ci(
                df,
                labels,
                ref,
                iterations=(
                    bootstrap_iterations
                ),
                seed=(
                    1701
                    + int(
                        tau_A * 100
                    ) * 10000
                    + int(
                        tau_C * 100
                    ) * 100
                    + int(
                        tau_V * 100
                    )
                ),
            )
        )

        rows.append(row)

    return pd.DataFrame(rows)


def calculate_scores(
    df,
    weights,
):
    scores = []

    for row in df.itertuples(
        index=False
    ):
        scores.append(
            danger_score(
                correctness=(
                    row.correctness
                ),
                expressed_confidence=(
                    row.expressed_confidence
                ),
                citation_appearance=(
                    row.citation_appearance
                ),
                citation_faithfulness=(
                    row.citation_faithfulness
                ),
                abstained=(
                    row.abstained
                ),
                weights=weights,
            )
        )

    return np.asarray(
        scores,
        dtype=float,
    )


def top_fraction_indices(
    values,
    fraction=0.10,
):
    values = np.asarray(
        values,
        dtype=float,
    )

    n = max(
        1,
        int(
            math.ceil(
                len(values)
                * fraction
            )
        ),
    )

    order = np.argsort(
        values,
        kind="stable",
    )

    return set(
        order[-n:].tolist()
    )


def weight_sensitivity(df):
    all_scores = {
        name: calculate_scores(
            df,
            weights,
        )
        for name, weights
        in WEIGHT_REGIMES.items()
    }

    reference = all_scores[
        "equal"
    ]

    ref_top = (
        top_fraction_indices(
            reference
        )
    )

    rows = []

    for name, scores in (
        all_scores.items()
    ):

        rho = spearmanr(
            reference,
            scores,
        ).statistic

        if np.isnan(rho):
            rho = float("nan")

        top = top_fraction_indices(
            scores
        )

        union = (
            ref_top | top
        )

        top_jaccard = (
            1.0
            if not union
            else len(
                ref_top & top
            ) / len(union)
        )

        rows.append({
            "weight_regime":
                name,

            "spearman_vs_equal":
                float(rho),

            "top_decile_jaccard":
                float(
                    top_jaccard
                ),

            "mean_absolute_score_change":
                float(
                    np.mean(
                        np.abs(
                            scores
                            - reference
                        )
                    )
                ),

            "mean_danger_score":
                float(
                    np.mean(scores)
                ),

            "median_danger_score":
                float(
                    np.median(scores)
                ),
        })

    return pd.DataFrame(rows)


def citation_unfaithful_sensitivity(
    df,
):
    sf = sf_labels(
        df,
        **REFERENCE,
    ).astype(bool)

    rows = []

    for tau_F in [
        0.40,
        0.50,
        0.60,
    ]:
        unfaithful = (
            sf
            & (
                df[
                    "citation_faithfulness"
                ].to_numpy()
                < tau_F
            )
        )

        rows.append({
            "tau_F":
                tau_F,

            "cusf_count":
                int(
                    unfaithful.sum()
                ),

            "cusf_rate_all_outputs":
                float(
                    unfaithful.mean()
                ),

            "fraction_of_sf_unfaithful":
                (
                    float(
                        unfaithful.sum()
                        / sf.sum()
                    )
                    if sf.sum() > 0
                    else float("nan")
                ),
        })

    return pd.DataFrame(rows)


def normalize_input(df):
    required = {
        "base_id",
        "model",
        "dataset",
        "condition",
        "correctness",
        "citation_appearance",
        "citation_faithfulness",
        "abstained",
    }

    missing = (
        required
        - set(df.columns)
    )

    if missing:
        raise ValueError(
            "Missing columns: "
            + ", ".join(
                sorted(missing)
            )
        )

    if (
        "expressed_confidence"
        not in df.columns
    ):
        if "confidence" not in df.columns:
            raise ValueError(
                "Need expressed_confidence "
                "or legacy confidence column"
            )

        df[
            "expressed_confidence"
        ] = df[
            "confidence"
        ].map(
            normalize_expressed_confidence
        )

    else:
        df[
            "expressed_confidence"
        ] = df[
            "expressed_confidence"
        ].map(
            normalize_expressed_confidence
        )

    for col in [
        "correctness",
        "citation_appearance",
        "citation_faithfulness",
    ]:
        df[col] = pd.to_numeric(
            df[col],
            errors="coerce",
        )

    if df[
        [
            "correctness",
            "citation_appearance",
        ]
    ].isna().any().any():
        raise ValueError(
            "Missing correctness or "
            "citation appearance values"
        )

    if df[
        "expressed_confidence"
    ].isna().any():
        raise ValueError(
            "Missing expressed confidence"
        )

    if df["abstained"].dtype != bool:
        mapping = {
            "true": True,
            "false": False,
            "1": True,
            "0": False,
            "yes": True,
            "no": False,
        }

        converted = (
            df["abstained"]
            .astype(str)
            .str.lower()
            .map(mapping)
        )

        if converted.isna().any():
            raise ValueError(
                "Could not parse abstained"
            )

        df["abstained"] = (
            converted.astype(bool)
        )

    # Faithfulness may be missing only for
    # abstentions or zero citation appearance.
    invalid_f = (
        df[
            "citation_faithfulness"
        ].isna()
        & (~df["abstained"])
        & (
            df[
                "citation_appearance"
            ] > 0
        )
    )

    if invalid_f.any():
        raise ValueError(
            "Missing citation faithfulness "
            "for cited non-abstaining output"
        )

    df[
        "citation_faithfulness"
    ] = df[
        "citation_faithfulness"
    ].fillna(1.0)

    return df


def run_analysis(
    df,
    out_dir,
    bootstrap_iterations=1000,
):
    out_dir = Path(
        out_dir
    )

    out_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    df = normalize_input(
        df.copy()
    )

    threshold_frames = []

    # Overall analysis.
    overall = threshold_sensitivity(
        df,
        bootstrap_iterations=(
            bootstrap_iterations
        ),
    )

    overall.insert(
        0,
        "scope_value",
        "ALL",
    )

    overall.insert(
        0,
        "scope",
        "overall",
    )

    threshold_frames.append(
        overall
    )

    # Model-specific stability.
    for model, group in df.groupby(
        "model",
        sort=True,
    ):
        model_result = (
            threshold_sensitivity(
                group,
                bootstrap_iterations=(
                    bootstrap_iterations
                ),
            )
        )

        model_result.insert(
            0,
            "scope_value",
            model,
        )

        model_result.insert(
            0,
            "scope",
            "model",
        )

        threshold_frames.append(
            model_result
        )

    threshold_df = pd.concat(
        threshold_frames,
        ignore_index=True,
    )

    threshold_df.to_csv(
        out_dir
        / "threshold_sensitivity_v3.csv",
        index=False,
    )

    weight_frames = []

    overall_weights = (
        weight_sensitivity(df)
    )

    overall_weights.insert(
        0,
        "scope_value",
        "ALL",
    )

    overall_weights.insert(
        0,
        "scope",
        "overall",
    )

    weight_frames.append(
        overall_weights
    )

    for model, group in df.groupby(
        "model",
        sort=True,
    ):
        w = weight_sensitivity(
            group
        )

        w.insert(
            0,
            "scope_value",
            model,
        )

        w.insert(
            0,
            "scope",
            "model",
        )

        weight_frames.append(w)

    weight_df = pd.concat(
        weight_frames,
        ignore_index=True,
    )

    weight_df.to_csv(
        out_dir
        / "weight_sensitivity_v3.csv",
        index=False,
    )

    cusf = (
        citation_unfaithful_sensitivity(
            df
        )
    )

    cusf.to_csv(
        out_dir
        / "citation_unfaithful_"
          "sensitivity_v3.csv",
        index=False,
    )

    metadata = {
        "rows": len(df),
        "models": sorted(
            df["model"]
            .astype(str)
            .unique()
            .tolist()
        ),
        "unique_base_ids":
            int(
                df[
                    "base_id"
                ].nunique()
            ),
        "threshold_settings":
            len(
                THRESHOLD_GRID
            ),
        "weight_regimes":
            list(
                WEIGHT_REGIMES
            ),
        "cluster_bootstrap_iterations":
            bootstrap_iterations,
    }

    (
        out_dir
        / "sensitivity_metadata_v3.json"
    ).write_text(
        json.dumps(
            metadata,
            indent=2,
        ),
        encoding="utf-8",
    )

    return (
        threshold_df,
        weight_df,
        cusf,
    )
