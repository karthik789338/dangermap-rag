import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, roc_auc_score
from sklearn.model_selection import StratifiedShuffleSplit


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


def safe_auc(y_true, scores):
    if len(np.unique(y_true)) < 2:
        return np.nan
    return roc_auc_score(y_true, scores)


def safe_pr_auc(y_true, scores):
    if len(np.unique(y_true)) < 2:
        return np.nan
    return average_precision_score(y_true, scores)


def save_fig(path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    plt.savefig(path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Saved figure: {path}")


def build_features(df: pd.DataFrame):
    out = pd.DataFrame(index=df.index)

    out["incorrectness"] = 1.0 - df["correctness"].astype(float)
    out["confidence_norm"] = df["confidence"].astype(float) / 100.0
    out["citation_appearance"] = df["citation_appearance"].astype(float)
    out["citation_misgrounding"] = 1.0 - df["citation_support_proxy"].astype(float)
    out["no_abstention"] = (~df["model_abstain"]).astype(float)
    out["abstention_failure"] = df["abstention_failure"].astype(float)

    return out


def shuffle_test(df: pd.DataFrame, seed: int = 42):
    rng = np.random.default_rng(seed)

    y = df["silent_failure"].astype(int).to_numpy()
    danger = df["danger_score"].astype(float).to_numpy()

    real_roc = safe_auc(y, danger)
    real_pr = safe_pr_auc(y, danger)

    shuffled = danger.copy()
    rng.shuffle(shuffled)

    shuffle_roc = safe_auc(y, shuffled)
    shuffle_pr = safe_pr_auc(y, shuffled)

    prevalence = float(np.mean(y))

    return {
        "real_roc_auc": real_roc,
        "real_pr_auc": real_pr,
        "shuffled_roc_auc": shuffle_roc,
        "shuffled_pr_auc": shuffle_pr,
        "silent_failure_prevalence": prevalence,
    }


def repeated_holdout_test(df: pd.DataFrame, n_splits: int = 10, test_size: float = 0.33, seed: int = 42):
    y = df["silent_failure"].astype(int).to_numpy()
    danger = df["danger_score"].astype(float).to_numpy()

    splitter = StratifiedShuffleSplit(
        n_splits=n_splits,
        test_size=test_size,
        random_state=seed,
    )

    rows = []

    for split_id, (_, test_idx) in enumerate(splitter.split(np.zeros(len(y)), y), start=1):
        y_test = y[test_idx]
        d_test = danger[test_idx]

        rows.append(
            {
                "split": split_id,
                "predictor": "Danger Score",
                "roc_auc": safe_auc(y_test, d_test),
                "pr_auc": safe_pr_auc(y_test, d_test),
            }
        )

    return pd.DataFrame(rows)


def logistic_regression_baseline(df: pd.DataFrame, n_splits: int = 10, test_size: float = 0.33, seed: int = 42):
    X = build_features(df)
    y = df["silent_failure"].astype(int).to_numpy()
    danger = df["danger_score"].astype(float).to_numpy()

    splitter = StratifiedShuffleSplit(
        n_splits=n_splits,
        test_size=test_size,
        random_state=seed,
    )

    rows = []

    for split_id, (train_idx, test_idx) in enumerate(splitter.split(X, y), start=1):
        X_train = X.iloc[train_idx]
        X_test = X.iloc[test_idx]
        y_train = y[train_idx]
        y_test = y[test_idx]

        model = LogisticRegression(
            max_iter=2000,
            solver="liblinear",
        )
        model.fit(X_train, y_train)

        lr_scores = model.predict_proba(X_test)[:, 1]
        danger_test = danger[test_idx]

        rows.append(
            {
                "split": split_id,
                "predictor": "Danger Score",
                "roc_auc": safe_auc(y_test, danger_test),
                "pr_auc": safe_pr_auc(y_test, danger_test),
            }
        )

        rows.append(
            {
                "split": split_id,
                "predictor": "Logistic Regression (components)",
                "roc_auc": safe_auc(y_test, lr_scores),
                "pr_auc": safe_pr_auc(y_test, lr_scores),
            }
        )

    return pd.DataFrame(rows)


def plot_distribution(df: pd.DataFrame, out_dir: Path):
    pos = df.loc[df["silent_failure"], "danger_score"].astype(float).to_numpy()
    neg = df.loc[~df["silent_failure"], "danger_score"].astype(float).to_numpy()

    plt.figure(figsize=(8, 5))
    bins = np.linspace(0, 1, 40)
    plt.hist(neg, bins=bins, alpha=0.6, density=True, label="SF = 0")
    plt.hist(pos, bins=bins, alpha=0.6, density=True, label="SF = 1")
    plt.xlabel("Danger Score")
    plt.ylabel("Density")
    plt.title("Danger Score distribution by Silent Failure label")
    plt.legend()
    save_fig(out_dir / "fig9_danger_score_distribution_by_sf.png")


def plot_holdout_comparison(df_holdout: pd.DataFrame, out_dir: Path):
    summary = (
        df_holdout.groupby("predictor")
        .agg(
            roc_auc_mean=("roc_auc", "mean"),
            roc_auc_std=("roc_auc", "std"),
            pr_auc_mean=("pr_auc", "mean"),
            pr_auc_std=("pr_auc", "std"),
        )
        .reset_index()
    )

    # ROC-AUC figure
    plt.figure(figsize=(7, 4.5))
    x = np.arange(len(summary))
    y = summary["roc_auc_mean"].to_numpy()
    err = summary["roc_auc_std"].fillna(0.0).to_numpy()

    plt.bar(x, y, yerr=err, capsize=4)
    plt.xticks(x, summary["predictor"].tolist(), rotation=15)
    plt.ylabel("ROC-AUC")
    plt.xlabel("Predictor")
    plt.title("Hold-out ROC-AUC comparison")
    save_fig(out_dir / "fig10_holdout_roc_auc_comparison.png")

    # PR-AUC figure
    plt.figure(figsize=(7, 4.5))
    y = summary["pr_auc_mean"].to_numpy()
    err = summary["pr_auc_std"].fillna(0.0).to_numpy()

    plt.bar(x, y, yerr=err, capsize=4)
    plt.xticks(x, summary["predictor"].tolist(), rotation=15)
    plt.ylabel("PR-AUC")
    plt.xlabel("Predictor")
    plt.title("Hold-out PR-AUC comparison")
    save_fig(out_dir / "fig11_holdout_pr_auc_comparison.png")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input_csv",
        default="outputs/qwen_7b_full_fever_finqa_scored_v2.csv",
    )
    parser.add_argument(
        "--out_dir",
        default="outputs/validation",
    )
    parser.add_argument("--n_splits", type=int, default=10)
    parser.add_argument("--test_size", type=float, default=0.33)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 80)
    print("DangerMap-RAG validation / sanity checks v2")
    print("=" * 80)

    df = pd.read_csv(args.input_csv)
    df = clean_dataframe(df)

    print("Rows:", len(df))
    print("Silent failure prevalence:", df["silent_failure"].mean())

    # 1) Shuffle test
    shuffle_res = shuffle_test(df, seed=args.seed)
    shuffle_df = pd.DataFrame([shuffle_res])
    shuffle_df.to_csv(out_dir / "shuffle_test_results_v2.csv", index=False)
    print("\nShuffle test:")
    print(shuffle_df.to_string(index=False))

    # 2) Danger Score stability on repeated hold-out test
    holdout_df = repeated_holdout_test(
        df,
        n_splits=args.n_splits,
        test_size=args.test_size,
        seed=args.seed,
    )
    holdout_df.to_csv(out_dir / "danger_score_holdout_results_v2.csv", index=False)

    print("\nRepeated hold-out results (Danger Score only):")
    holdout_summary = pd.DataFrame([{
        "roc_auc_mean": holdout_df["roc_auc"].mean(),
        "roc_auc_std": holdout_df["roc_auc"].std(),
        "pr_auc_mean": holdout_df["pr_auc"].mean(),
        "pr_auc_std": holdout_df["pr_auc"].std(),
    }])
    holdout_summary.to_csv(out_dir / "danger_score_holdout_summary_v2.csv", index=False)
    print(holdout_summary.to_string(index=False))

    # 3) Logistic regression baseline
    baseline_df = logistic_regression_baseline(
        df,
        n_splits=args.n_splits,
        test_size=args.test_size,
        seed=args.seed,
    )
    baseline_df.to_csv(out_dir / "logistic_baseline_comparison_v2.csv", index=False)

    baseline_summary = (
        baseline_df.groupby("predictor")
        .agg(
            roc_auc_mean=("roc_auc", "mean"),
            roc_auc_std=("roc_auc", "std"),
            pr_auc_mean=("pr_auc", "mean"),
            pr_auc_std=("pr_auc", "std"),
        )
        .reset_index()
    )
    baseline_summary.to_csv(out_dir / "logistic_baseline_summary_v2.csv", index=False)

    print("\nDanger Score vs logistic regression baseline:")
    print(baseline_summary.to_string(index=False))

    # 4) Distributions and comparison figures
    plot_distribution(df, out_dir)
    plot_holdout_comparison(baseline_df, out_dir)

    print("\nSaved outputs:")
    print(out_dir / "shuffle_test_results_v2.csv")
    print(out_dir / "danger_score_holdout_results_v2.csv")
    print(out_dir / "logistic_baseline_comparison_v2.csv")
    print(out_dir / "logistic_baseline_summary_v2.csv")
    print(out_dir / "fig9_danger_score_distribution_by_sf.png")
    print(out_dir / "fig10_holdout_roc_auc_comparison.png")
    print(out_dir / "fig11_holdout_pr_auc_comparison.png")


if __name__ == "__main__":
    main()
