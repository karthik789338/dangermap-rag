import argparse
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import average_precision_score, roc_auc_score


BOOL_COLS = [
    "silent_failure",
    "citation_valid_wrong",
    "abstention_failure",
    "model_abstain",
    "expected_abstain",
]


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


def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    for col in BOOL_COLS:
        if col in df.columns:
            df[col] = ensure_bool(df[col])

    numeric_cols = [
        "correctness",
        "confidence",
        "danger_score",
        "citation_appearance",
        "citation_support_proxy",
        "citation_misgrounding_proxy",
    ]

    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)

    return df


def bootstrap_metric_ci(y_true, scores, metric_fn, iters=1000, seed=42):
    rng = np.random.default_rng(seed)
    y_true = np.asarray(y_true)
    scores = np.asarray(scores)

    vals = []
    n = len(y_true)

    for _ in range(iters):
        idx = rng.integers(0, n, size=n)
        y_b = y_true[idx]
        s_b = scores[idx]

        # ROC-AUC is undefined if bootstrap sample has only one class.
        if len(np.unique(y_b)) < 2:
            continue

        try:
            vals.append(metric_fn(y_b, s_b))
        except Exception:
            continue

    if not vals:
        return np.nan, np.nan

    return float(np.percentile(vals, 2.5)), float(np.percentile(vals, 97.5))


def safe_auc(y_true, scores):
    if len(np.unique(y_true)) < 2:
        return np.nan
    return roc_auc_score(y_true, scores)


def safe_pr_auc(y_true, scores):
    if len(np.unique(y_true)) < 2:
        return np.nan
    return average_precision_score(y_true, scores)


def build_predictors(df: pd.DataFrame) -> dict:
    """
    All predictors are oriented so higher = more likely silent failure.
    """
    predictors = {}

    predictors["Danger Score"] = df["danger_score"].astype(float)

    predictors["Confidence only"] = df["confidence"].astype(float) / 100.0

    predictors["Incorrectness only (1 - correctness)"] = 1.0 - df["correctness"].astype(float)

    predictors["Citation misgrounding only (1 - citation support)"] = (
        1.0 - df["citation_support_proxy"].astype(float)
    )

    predictors["Citation appearance only"] = df["citation_appearance"].astype(float)

    # The user's requested "abstention indicator only".
    # Silent failures are non-abstaining by definition, so this is expected to be strong
    # but partially tautological. We keep it for component comparison.
    predictors["No-abstention indicator only"] = (~df["model_abstain"]).astype(float)

    # Optional stricter component using expected abstention, but this uses benchmark labels.
    # It should be reported separately or in appendix, not as a deployable detector.
    predictors["Abstention failure indicator only"] = df["abstention_failure"].astype(float)

    return predictors


def evaluate_predictors(df: pd.DataFrame, group_cols, bootstrap_iters, seed):
    rows = []

    if group_cols:
        grouped = df.groupby(group_cols, dropna=False)
    else:
        grouped = [((), df)]

    for group_key, g in grouped:
        if not isinstance(group_key, tuple):
            group_key = (group_key,)

        y_true = g["silent_failure"].astype(int).to_numpy()
        prevalence = float(np.mean(y_true)) if len(y_true) else 0.0

        predictors = build_predictors(g)

        for pred_name, scores in predictors.items():
            scores = np.asarray(scores, dtype=float)

            roc_auc = safe_auc(y_true, scores)
            pr_auc = safe_pr_auc(y_true, scores)

            roc_lo, roc_hi = bootstrap_metric_ci(
                y_true,
                scores,
                safe_auc,
                iters=bootstrap_iters,
                seed=seed,
            )

            pr_lo, pr_hi = bootstrap_metric_ci(
                y_true,
                scores,
                safe_pr_auc,
                iters=bootstrap_iters,
                seed=seed + 1,
            )

            row = {}

            for col, val in zip(group_cols, group_key):
                row[col] = val

            row.update(
                {
                    "predictor": pred_name,
                    "n": len(g),
                    "silent_failure_prevalence": prevalence,
                    "roc_auc": roc_auc,
                    "roc_auc_ci95_low": roc_lo,
                    "roc_auc_ci95_high": roc_hi,
                    "pr_auc": pr_auc,
                    "pr_auc_ci95_low": pr_lo,
                    "pr_auc_ci95_high": pr_hi,
                }
            )

            rows.append(row)

    out = pd.DataFrame(rows)
    if len(out):
        out = out.sort_values(["roc_auc", "pr_auc"], ascending=False).reset_index(drop=True)

    return out


def add_display_cols(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    for col in ["silent_failure_prevalence", "roc_auc", "pr_auc"]:
        if col in df.columns:
            df[col + "_display"] = df[col].map(lambda x: "" if pd.isna(x) else f"{x:.3f}")

    for col in ["roc_auc", "pr_auc"]:
        lo = col + "_ci95_low"
        hi = col + "_ci95_high"
        if lo in df.columns and hi in df.columns:
            df[col + "_ci95_display"] = df.apply(
                lambda r: "" if pd.isna(r[lo]) else f"[{r[lo]:.3f}, {r[hi]:.3f}]",
                axis=1,
            )

    return df


def save(df, path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
    print(f"Saved: {path} ({len(df)} rows)")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input_csv",
        default="outputs/qwen_7b_full_fever_finqa_scored_v2.csv",
    )
    parser.add_argument(
        "--out_dir",
        default="outputs/metric_comparison",
    )
    parser.add_argument("--bootstrap_iters", type=int, default=1000)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    out_dir = Path(args.out_dir)

    print("=" * 80)
    print("DangerMap-RAG metric comparison v2")
    print("=" * 80)

    df = pd.read_csv(args.input_csv)
    df = clean_dataframe(df)

    print("Rows:", len(df))
    print("Silent failure prevalence:", df["silent_failure"].mean())

    overall = evaluate_predictors(
        df,
        group_cols=[],
        bootstrap_iters=args.bootstrap_iters,
        seed=args.seed,
    )

    by_domain = evaluate_predictors(
        df,
        group_cols=["domain"],
        bootstrap_iters=args.bootstrap_iters,
        seed=args.seed,
    )

    by_condition = evaluate_predictors(
        df,
        group_cols=["condition"],
        bootstrap_iters=args.bootstrap_iters,
        seed=args.seed,
    )

    by_domain_condition = evaluate_predictors(
        df,
        group_cols=["domain", "condition"],
        bootstrap_iters=args.bootstrap_iters,
        seed=args.seed,
    )

    save(add_display_cols(overall), out_dir / "metric_comparison_overall_v2.csv")
    save(add_display_cols(by_domain), out_dir / "metric_comparison_by_domain_v2.csv")
    save(add_display_cols(by_condition), out_dir / "metric_comparison_by_condition_v2.csv")
    save(add_display_cols(by_domain_condition), out_dir / "metric_comparison_by_domain_condition_v2.csv")

    print("\nOverall metric comparison:")
    cols = [
        "predictor",
        "n",
        "silent_failure_prevalence",
        "roc_auc",
        "roc_auc_ci95_low",
        "roc_auc_ci95_high",
        "pr_auc",
        "pr_auc_ci95_low",
        "pr_auc_ci95_high",
    ]
    print(overall[cols].to_string(index=False))

    print("\nBest predictor by domain:")
    best_domain = (
        by_domain.sort_values(["domain", "roc_auc"], ascending=[True, False])
        .groupby("domain")
        .head(1)
    )
    print(best_domain[["domain", "predictor", "roc_auc", "pr_auc"]].to_string(index=False))

    print("\nBest predictor by condition:")
    best_condition = (
        by_condition.sort_values(["condition", "roc_auc"], ascending=[True, False])
        .groupby("condition")
        .head(1)
    )
    print(best_condition[["condition", "predictor", "roc_auc", "pr_auc"]].to_string(index=False))


if __name__ == "__main__":
    main()
