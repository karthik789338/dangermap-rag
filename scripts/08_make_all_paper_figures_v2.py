import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


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


def load_scored_csv(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)

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


def save_fig(path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    plt.savefig(path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Saved: {path}")


def add_bar_labels(ax, values, fmt="{:.1f}%"):
    ymax = max(values) if len(values) else 0
    offset = max(0.01, ymax * 0.02)

    for i, v in enumerate(values):
        ax.text(i, v + offset, fmt.format(v), ha="center", va="bottom", fontsize=9)


def add_bar_labels_horizontal(ax, values, fmt="{:.3f}"):
    for i, v in enumerate(values):
        ax.text(v + 0.01, i, fmt.format(v), va="center", fontsize=9)


def fig1_silent_failure_by_domain(df: pd.DataFrame, out_dir: Path):
    summary = (
        df.groupby("domain", dropna=False)
        .agg(
            n=("instance_id", "count"),
            silent_failure_rate=("silent_failure", "mean"),
        )
        .reset_index()
        .sort_values("silent_failure_rate", ascending=False)
    )

    x = np.arange(len(summary))
    y = 100 * summary["silent_failure_rate"].to_numpy()

    plt.figure(figsize=(8, 5))
    plt.bar(x, y)
    plt.xticks(x, summary["domain"].tolist())
    plt.ylabel("Silent failure rate (%)")
    plt.xlabel("Domain")
    plt.title("Silent failure rate by domain")
    add_bar_labels(plt.gca(), y)
    save_fig(out_dir / "fig1_silent_failure_by_domain.png")


def fig2_silent_failure_by_condition(df: pd.DataFrame, out_dir: Path):
    order = ["missing", "partial", "clean", "noisy", "stale", "contradictory"]

    summary = (
        df.groupby("condition", dropna=False)
        .agg(
            n=("instance_id", "count"),
            silent_failure_rate=("silent_failure", "mean"),
        )
        .reset_index()
    )

    summary["condition"] = pd.Categorical(summary["condition"], categories=order, ordered=True)
    summary = summary.sort_values("condition")

    x = np.arange(len(summary))
    y = 100 * summary["silent_failure_rate"].to_numpy()

    plt.figure(figsize=(9, 5))
    plt.bar(x, y)
    plt.xticks(x, summary["condition"].tolist(), rotation=20)
    plt.ylabel("Silent failure rate (%)")
    plt.xlabel("Perturbation condition")
    plt.title("Silent failure rate by evidence condition")
    add_bar_labels(plt.gca(), y)
    save_fig(out_dir / "fig2_silent_failure_by_condition.png")


def fig3_abstention_failure_by_condition(df: pd.DataFrame, out_dir: Path):
    order = ["missing", "partial", "clean", "noisy", "stale", "contradictory"]

    summary = (
        df.groupby("condition", dropna=False)
        .agg(
            n=("instance_id", "count"),
            abstention_failure_rate=("abstention_failure", "mean"),
        )
        .reset_index()
    )

    summary["condition"] = pd.Categorical(summary["condition"], categories=order, ordered=True)
    summary = summary.sort_values("condition")

    x = np.arange(len(summary))
    y = 100 * summary["abstention_failure_rate"].to_numpy()

    plt.figure(figsize=(9, 5))
    plt.bar(x, y)
    plt.xticks(x, summary["condition"].tolist(), rotation=20)
    plt.ylabel("Abstention failure rate (%)")
    plt.xlabel("Perturbation condition")
    plt.title("Abstention failure rate by evidence condition")
    add_bar_labels(plt.gca(), y)
    save_fig(out_dir / "fig3_abstention_failure_by_condition.png")


def fig4_top_risk_zones(top_risk_csv: str, out_dir: Path, top_n: int = 15):
    df = pd.read_csv(top_risk_csv).head(top_n).copy()

    df["zone"] = df["domain"] + " | " + df["dataset"] + " | " + df["condition"]
    df = df.iloc[::-1]

    y = 100 * df["silent_failure_rate"].to_numpy()
    labels = df["zone"].tolist()

    plt.figure(figsize=(11, 8))
    plt.barh(np.arange(len(df)), y)
    plt.yticks(np.arange(len(df)), labels)
    plt.xlabel("Silent failure rate (%)")
    plt.ylabel("Risk zone")
    plt.title(f"Top {top_n} highest-risk zones")
    save_fig(out_dir / "fig4_top_risk_zones.png")


def fig5_domain_condition_heatmap(df: pd.DataFrame, out_dir: Path):
    row_order = ["legal", "finance", "medical", "general"]
    col_order = ["missing", "partial", "clean", "noisy", "stale", "contradictory"]

    pivot = (
        df.groupby(["domain", "condition"], dropna=False)["silent_failure"]
        .mean()
        .reset_index()
        .pivot(index="domain", columns="condition", values="silent_failure")
    )

    pivot = pivot.reindex(index=row_order, columns=col_order)

    arr = pivot.to_numpy() * 100.0

    plt.figure(figsize=(10, 5))
    im = plt.imshow(arr, aspect="auto")
    plt.colorbar(im, label="Silent failure rate (%)")
    plt.xticks(np.arange(len(col_order)), col_order, rotation=20)
    plt.yticks(np.arange(len(row_order)), row_order)
    plt.title("Silent failure heatmap by domain and condition")

    for i in range(arr.shape[0]):
        for j in range(arr.shape[1]):
            if not np.isnan(arr[i, j]):
                plt.text(j, i, f"{arr[i, j]:.1f}", ha="center", va="center", fontsize=9)

    save_fig(out_dir / "fig5_domain_condition_heatmap.png")


def fig6_confidence_vs_correctness(df: pd.DataFrame, out_dir: Path, sample_n: int = 4000):
    if len(df) > sample_n:
        plot_df = df.sample(sample_n, random_state=42).copy()
    else:
        plot_df = df.copy()

    x = plot_df["confidence"].to_numpy()
    y = plot_df["correctness"].to_numpy()

    plt.figure(figsize=(8, 6))
    plt.scatter(x, y, alpha=0.25, s=16)
    plt.xlabel("Model confidence")
    plt.ylabel("Correctness")
    plt.title("Confidence vs correctness")
    plt.ylim(-0.02, 1.02)
    plt.xlim(-1, 101)
    save_fig(out_dir / "fig6_confidence_vs_correctness.png")


def clean_metric_predictor_order(df: pd.DataFrame) -> pd.DataFrame:
    order = [
        "Danger Score",
        "Incorrectness only (1 - correctness)",
        "Confidence only",
        "Citation misgrounding only (1 - citation support)",
        "Abstention failure indicator only",
        "Citation appearance only",
        "No-abstention indicator only",
    ]

    df = df.copy()
    df["predictor"] = pd.Categorical(df["predictor"], categories=order, ordered=True)
    return df.sort_values("predictor")


def fig7_metric_roc_auc(metric_csv: str, out_dir: Path):
    df = pd.read_csv(metric_csv)
    df = clean_metric_predictor_order(df)

    y_pos = np.arange(len(df))
    values = df["roc_auc"].to_numpy()

    plt.figure(figsize=(10, 5.5))
    plt.barh(y_pos, values)
    plt.yticks(y_pos, df["predictor"].astype(str).tolist())
    plt.xlabel("ROC-AUC")
    plt.ylabel("Predictor")
    plt.title("ROC-AUC for predicting Silent Failure")
    add_bar_labels_horizontal(plt.gca(), values)
    plt.xlim(0, 1.03)
    save_fig(out_dir / "fig7_metric_comparison_roc_auc.png")


def fig8_metric_pr_auc(metric_csv: str, out_dir: Path):
    df = pd.read_csv(metric_csv)
    df = clean_metric_predictor_order(df)

    y_pos = np.arange(len(df))
    values = df["pr_auc"].to_numpy()

    plt.figure(figsize=(10, 5.5))
    plt.barh(y_pos, values)
    plt.yticks(y_pos, df["predictor"].astype(str).tolist())
    plt.xlabel("PR-AUC")
    plt.ylabel("Predictor")
    plt.title("PR-AUC for predicting Silent Failure")
    add_bar_labels_horizontal(plt.gca(), values)
    plt.xlim(0, 1.03)
    save_fig(out_dir / "fig8_metric_comparison_pr_auc.png")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--scored_csv",
        default="outputs/qwen_7b_full_fever_finqa_scored_v2.csv",
    )
    parser.add_argument(
        "--top_risk_csv",
        default="outputs/tables/table_top_risk_zones_v2.csv",
    )
    parser.add_argument(
        "--metric_csv",
        default="outputs/metric_comparison/metric_comparison_overall_v2.csv",
    )
    parser.add_argument(
        "--out_dir",
        default="outputs/figures",
    )
    args = parser.parse_args()

    out_dir = Path(args.out_dir)

    print("=" * 80)
    print("DangerMap-RAG full paper figure builder v2")
    print("=" * 80)
    print("Scored CSV:", args.scored_csv)
    print("Top risk CSV:", args.top_risk_csv)
    print("Metric CSV:", args.metric_csv)
    print("Output dir:", out_dir)

    df = load_scored_csv(args.scored_csv)
    print("Rows:", len(df))

    fig1_silent_failure_by_domain(df, out_dir)
    fig2_silent_failure_by_condition(df, out_dir)
    fig3_abstention_failure_by_condition(df, out_dir)
    fig4_top_risk_zones(args.top_risk_csv, out_dir, top_n=15)
    fig5_domain_condition_heatmap(df, out_dir)
    fig6_confidence_vs_correctness(df, out_dir)
    fig7_metric_roc_auc(args.metric_csv, out_dir)
    fig8_metric_pr_auc(args.metric_csv, out_dir)

    print("\nDone. Generated Figures 1-8.")


if __name__ == "__main__":
    main()
