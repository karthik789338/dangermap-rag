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


def add_bar_labels_horizontal(ax, values, fmt="{:.3f}"):
    for i, v in enumerate(values):
        ax.text(v + 0.01, i, fmt.format(v), va="center", fontsize=9)


def clean_predictor_names(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    order = [
        "Danger Score",
        "Incorrectness only (1 - correctness)",
        "Confidence only",
        "Citation misgrounding only (1 - citation support)",
        "Abstention failure indicator only",
        "Citation appearance only",
        "No-abstention indicator only",
    ]

    df["predictor"] = pd.Categorical(df["predictor"], categories=order, ordered=True)
    df = df.sort_values("predictor")
    return df


def fig7_roc_auc(metric_csv: str, out_dir: Path):
    df = pd.read_csv(metric_csv)
    df = clean_predictor_names(df)

    y = np.arange(len(df))
    x = df["roc_auc"].to_numpy()

    plt.figure(figsize=(10, 5.5))
    plt.barh(y, x)

    plt.yticks(y, df["predictor"].astype(str).tolist())
    plt.xlabel("ROC-AUC")
    plt.ylabel("Predictor")
    plt.title("Figure 7. ROC-AUC for predicting Silent Failure")

    add_bar_labels_horizontal(plt.gca(), x)

    plt.xlim(0, min(1.02, max(1.0, x.max() + 0.05)))

    save_fig(out_dir / "fig7_metric_comparison_roc_auc.png")


def fig8_pr_auc(metric_csv: str, out_dir: Path):
    df = pd.read_csv(metric_csv)
    df = clean_predictor_names(df)

    y = np.arange(len(df))
    x = df["pr_auc"].to_numpy()

    plt.figure(figsize=(10, 5.5))
    plt.barh(y, x)

    plt.yticks(y, df["predictor"].astype(str).tolist())
    plt.xlabel("PR-AUC")
    plt.ylabel("Predictor")
    plt.title("Figure 8. PR-AUC for predicting Silent Failure")

    add_bar_labels_horizontal(plt.gca(), x)

    plt.xlim(0, min(1.02, max(1.0, x.max() + 0.05)))

    save_fig(out_dir / "fig8_metric_comparison_pr_auc.png")


def main():
    parser = argparse.ArgumentParser()
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
    print("DangerMap-RAG metric figure builder v2")
    print("=" * 80)
    print("Input metric CSV:", args.metric_csv)
    print("Output dir:", out_dir)

    fig7_roc_auc(args.metric_csv, out_dir)
    fig8_pr_auc(args.metric_csv, out_dir)

    print("\nDone.")


if __name__ == "__main__":
    main()
