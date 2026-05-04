import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def save_fig(path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    plt.savefig(path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Saved: {path}")


def add_labels(ax, values, fmt="{:.1f}%"):
    ymax = max(values) if len(values) else 0
    offset = max(0.01, ymax * 0.02)
    for i, v in enumerate(values):
        ax.text(i, v + offset, fmt.format(v), ha="center", va="bottom", fontsize=9)


def bar_metric(df, metric, ylabel, title, out_path, percent=True):
    df = df.sort_values(metric, ascending=False).copy()
    x = np.arange(len(df))
    y = df[metric].to_numpy()

    if percent:
        y_plot = 100 * y
    else:
        y_plot = y

    plt.figure(figsize=(8, 5))
    plt.bar(x, y_plot)
    plt.xticks(x, df["model_tag"].tolist(), rotation=15)
    plt.ylabel(ylabel)
    plt.xlabel("Model")
    plt.title(title)

    if percent:
        add_labels(plt.gca(), y_plot, fmt="{:.1f}%")
    else:
        add_labels(plt.gca(), y_plot, fmt="{:.3f}")

    save_fig(out_path)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--overall_csv",
        default="outputs/model_comparison/model_comparison_overall_v2.csv",
    )
    parser.add_argument(
        "--by_condition_csv",
        default="outputs/model_comparison/model_comparison_by_condition_v2.csv",
    )
    parser.add_argument(
        "--by_domain_csv",
        default="outputs/model_comparison/model_comparison_by_domain_v2.csv",
    )
    parser.add_argument(
        "--out_dir",
        default="outputs/model_comparison/figures",
    )
    args = parser.parse_args()

    out_dir = Path(args.out_dir)

    overall = pd.read_csv(args.overall_csv)
    by_condition = pd.read_csv(args.by_condition_csv)
    by_domain = pd.read_csv(args.by_domain_csv)

    bar_metric(
        overall,
        metric="silent_failure_rate",
        ylabel="Silent failure rate (%)",
        title="Silent failure rate by model",
        out_path=out_dir / "fig_model_silent_failure_rate.png",
        percent=True,
    )

    bar_metric(
        overall,
        metric="citation_valid_wrong_rate",
        ylabel="Citation-valid wrong rate (%)",
        title="Citation-valid wrong-answer rate by model",
        out_path=out_dir / "fig_model_citation_valid_wrong_rate.png",
        percent=True,
    )

    bar_metric(
        overall,
        metric="abstention_failure_rate",
        ylabel="Abstention failure rate (%)",
        title="Abstention failure rate by model",
        out_path=out_dir / "fig_model_abstention_failure_rate.png",
        percent=True,
    )

    bar_metric(
        overall,
        metric="avg_correctness",
        ylabel="Average correctness (%)",
        title="Average correctness by model",
        out_path=out_dir / "fig_model_avg_correctness.png",
        percent=True,
    )

    # Heatmap: model x condition silent failure
    pivot = by_condition.pivot(index="model_tag", columns="condition", values="silent_failure_rate")
    col_order = ["missing", "partial", "clean", "noisy", "stale", "contradictory"]
    pivot = pivot.reindex(columns=col_order)
    arr = pivot.to_numpy() * 100

    plt.figure(figsize=(10, 4.5))
    im = plt.imshow(arr, aspect="auto")
    plt.colorbar(im, label="Silent failure rate (%)")
    plt.xticks(np.arange(len(pivot.columns)), pivot.columns.tolist(), rotation=20)
    plt.yticks(np.arange(len(pivot.index)), pivot.index.tolist())
    plt.title("Silent failure heatmap by model and condition")

    for i in range(arr.shape[0]):
        for j in range(arr.shape[1]):
            if not np.isnan(arr[i, j]):
                plt.text(j, i, f"{arr[i, j]:.1f}", ha="center", va="center", fontsize=9)

    save_fig(out_dir / "fig_model_condition_silent_failure_heatmap.png")

    # Heatmap: model x domain silent failure
    pivot = by_domain.pivot(index="model_tag", columns="domain", values="silent_failure_rate")
    domain_order = ["legal", "finance", "medical", "general"]
    pivot = pivot.reindex(columns=domain_order)
    arr = pivot.to_numpy() * 100

    plt.figure(figsize=(8, 4.5))
    im = plt.imshow(arr, aspect="auto")
    plt.colorbar(im, label="Silent failure rate (%)")
    plt.xticks(np.arange(len(pivot.columns)), pivot.columns.tolist(), rotation=20)
    plt.yticks(np.arange(len(pivot.index)), pivot.index.tolist())
    plt.title("Silent failure heatmap by model and domain")

    for i in range(arr.shape[0]):
        for j in range(arr.shape[1]):
            if not np.isnan(arr[i, j]):
                plt.text(j, i, f"{arr[i, j]:.1f}", ha="center", va="center", fontsize=9)

    save_fig(out_dir / "fig_model_domain_silent_failure_heatmap.png")

    print("Done.")


if __name__ == "__main__":
    main()
