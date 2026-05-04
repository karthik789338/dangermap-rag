import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


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

    bool_cols = [
        "silent_failure",
        "citation_valid_wrong",
        "abstention_failure",
        "model_abstain",
        "expected_abstain",
    ]
    for col in bool_cols:
        if col in df.columns:
            df[col] = ensure_bool(df[col])

    num_cols = [
        "correctness",
        "confidence",
        "danger_score",
        "citation_appearance",
        "citation_support_proxy",
        "citation_misgrounding_proxy",
    ]
    for col in num_cols:
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
    plt.title("Silent failure rate by domain (v2)")
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
    plt.xlabel("Condition")
    plt.title("Silent failure rate by perturbation condition (v2)")
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
    plt.xlabel("Condition")
    plt.title("Abstention failure rate by perturbation condition (v2)")
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
    plt.title(f"Top {top_n} highest-risk zones (v2)")
    save_fig(out_dir / "fig4_top_risk_zones.png")


def fig5_domain_condition_heatmap(df: pd.DataFrame, out_dir: Path):
    order_rows = ["legal", "finance", "medical", "general"]
    order_cols = ["missing", "partial", "clean", "noisy", "stale", "contradictory"]

    pivot = (
        df.groupby(["domain", "condition"], dropna=False)["silent_failure"]
        .mean()
        .reset_index()
        .pivot(index="domain", columns="condition", values="silent_failure")
    )

    pivot = pivot.reindex(index=order_rows, columns=order_cols)

    arr = pivot.to_numpy() * 100.0

    plt.figure(figsize=(10, 5))
    im = plt.imshow(arr, aspect="auto")
    plt.colorbar(im, label="Silent failure rate (%)")
    plt.xticks(np.arange(len(order_cols)), order_cols, rotation=20)
    plt.yticks(np.arange(len(order_rows)), order_rows)
    plt.title("Silent failure heatmap by domain and condition (v2)")

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
    plt.title("Confidence vs correctness (sampled, v2)")
    plt.ylim(-0.02, 1.02)
    plt.xlim(-1, 101)
    save_fig(out_dir / "fig6_confidence_vs_correctness.png")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input_csv",
        default="outputs/qwen_7b_full_fever_finqa_scored_v2.csv",
    )
    parser.add_argument(
        "--top_risk_csv",
        default="outputs/tables/table_top_risk_zones_v2.csv",
    )
    parser.add_argument(
        "--out_dir",
        default="outputs/figures",
    )
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    df = load_scored_csv(args.input_csv)

    print("=" * 80)
    print("DangerMap-RAG paper figure builder v2")
    print("=" * 80)
    print("Input scored CSV:", args.input_csv)
    print("Input top-risk CSV:", args.top_risk_csv)
    print("Output dir:", out_dir)
    print("Rows:", len(df))

    fig1_silent_failure_by_domain(df, out_dir)
    fig2_silent_failure_by_condition(df, out_dir)
    fig3_abstention_failure_by_condition(df, out_dir)
    fig4_top_risk_zones(args.top_risk_csv, out_dir, top_n=15)
    fig5_domain_condition_heatmap(df, out_dir)
    fig6_confidence_vs_correctness(df, out_dir)

    print("\nDone.")


if __name__ == "__main__":
    main()
