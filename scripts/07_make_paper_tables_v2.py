import argparse
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd


BOOL_COLS = [
    "silent_failure",
    "citation_valid_wrong",
    "abstention_failure",
    "model_abstain",
    "expected_abstain",
]

METRICS = {
    "silent_failure_rate": ("silent_failure", "mean"),
    "citation_valid_wrong_rate": ("citation_valid_wrong", "mean"),
    "abstention_failure_rate": ("abstention_failure", "mean"),
    "abstention_rate": ("model_abstain", "mean"),
    "avg_correctness": ("correctness", "mean"),
    "avg_confidence": ("confidence", "mean"),
    "avg_danger_score": ("danger_score", "mean"),
    "avg_citation_appearance": ("citation_appearance", "mean"),
    "avg_citation_support": ("citation_support_proxy", "mean"),
}


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


def bootstrap_ci(values: np.ndarray, rng: np.random.Generator, iters: int = 1000) -> Tuple[float, float]:
    values = np.asarray(values, dtype=float)

    if len(values) == 0:
        return 0.0, 0.0

    if len(values) == 1:
        return float(values[0]), float(values[0])

    idx = rng.integers(0, len(values), size=(iters, len(values)))
    boot_means = values[idx].mean(axis=1)

    lo = np.percentile(boot_means, 2.5)
    hi = np.percentile(boot_means, 97.5)

    return float(lo), float(hi)


def summarize_group(
    df: pd.DataFrame,
    group_cols: List[str],
    bootstrap_iters: int,
    seed: int,
) -> pd.DataFrame:
    rows = []
    rng = np.random.default_rng(seed)

    if group_cols:
        grouped = df.groupby(group_cols, dropna=False)
    else:
        grouped = [((), df)]

    for group_key, g in grouped:
        if not isinstance(group_key, tuple):
            group_key = (group_key,)

        row: Dict[str, object] = {}

        for col, val in zip(group_cols, group_key):
            row[col] = val

        row["n"] = len(g)

        for metric_name, (source_col, agg_type) in METRICS.items():
            if source_col not in g.columns:
                continue

            values = g[source_col].astype(float).to_numpy()

            if agg_type == "mean":
                mean_val = float(np.mean(values)) if len(values) else 0.0
            else:
                raise ValueError(f"Unsupported agg type: {agg_type}")

            ci_lo, ci_hi = bootstrap_ci(values, rng, iters=bootstrap_iters)

            row[metric_name] = mean_val
            row[f"{metric_name}_ci95_low"] = ci_lo
            row[f"{metric_name}_ci95_high"] = ci_hi

        rows.append(row)

    out = pd.DataFrame(rows)

    sort_cols = []
    for c in ["silent_failure_rate", "avg_danger_score", "abstention_failure_rate"]:
        if c in out.columns:
            sort_cols.append(c)

    if sort_cols:
        out = out.sort_values(sort_cols, ascending=False)

    return out.reset_index(drop=True)


def add_percentage_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    rate_cols = [
        "silent_failure_rate",
        "citation_valid_wrong_rate",
        "abstention_failure_rate",
        "abstention_rate",
        "avg_correctness",
        "avg_confidence",
        "avg_danger_score",
        "avg_citation_appearance",
        "avg_citation_support",
    ]

    for col in rate_cols:
        if col not in df.columns:
            continue

        if col == "avg_confidence":
            df[col + "_display"] = df[col].map(lambda x: f"{x:.2f}")
        else:
            df[col + "_display"] = df[col].map(lambda x: f"{100 * x:.2f}%")

        low = col + "_ci95_low"
        high = col + "_ci95_high"

        if low in df.columns and high in df.columns:
            if col == "avg_confidence":
                df[col + "_ci95_display"] = df.apply(
                    lambda r: f"[{r[low]:.2f}, {r[high]:.2f}]",
                    axis=1,
                )
            else:
                df[col + "_ci95_display"] = df.apply(
                    lambda r: f"[{100 * r[low]:.2f}%, {100 * r[high]:.2f}%]",
                    axis=1,
                )

    return df


def make_top_risk_zones(df: pd.DataFrame, bootstrap_iters: int, seed: int, top_n: int) -> pd.DataFrame:
    grouped = summarize_group(
        df,
        group_cols=["domain", "dataset", "condition"],
        bootstrap_iters=bootstrap_iters,
        seed=seed,
    )

    risk_cols = [
        "domain",
        "dataset",
        "condition",
        "n",
        "silent_failure_rate",
        "silent_failure_rate_ci95_low",
        "silent_failure_rate_ci95_high",
        "citation_valid_wrong_rate",
        "abstention_failure_rate",
        "avg_correctness",
        "avg_confidence",
        "avg_danger_score",
        "avg_citation_appearance",
        "avg_citation_support",
    ]

    risk_cols = [c for c in risk_cols if c in grouped.columns]

    return grouped[risk_cols].head(top_n).reset_index(drop=True)


def save_table(df: pd.DataFrame, path: Path) -> None:
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
        default="outputs/tables",
    )
    parser.add_argument("--bootstrap_iters", type=int, default=1000)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--top_n", type=int, default=25)
    args = parser.parse_args()

    out_dir = Path(args.out_dir)

    print("=" * 80)
    print("DangerMap-RAG paper table builder v2")
    print("=" * 80)
    print("Input:", args.input_csv)
    print("Output dir:", out_dir)
    print("Bootstrap iterations:", args.bootstrap_iters)

    df = pd.read_csv(args.input_csv)
    df = clean_dataframe(df)

    print("Rows:", len(df))
    print("Domains:", sorted(df["domain"].unique()))
    print("Conditions:", sorted(df["condition"].unique()))

    overall = summarize_group(df, [], args.bootstrap_iters, args.seed)
    by_domain = summarize_group(df, ["domain"], args.bootstrap_iters, args.seed)
    by_condition = summarize_group(df, ["condition"], args.bootstrap_iters, args.seed)
    by_dataset = summarize_group(df, ["domain", "dataset"], args.bootstrap_iters, args.seed)
    by_dataset_condition = summarize_group(
        df,
        ["domain", "dataset", "condition"],
        args.bootstrap_iters,
        args.seed,
    )
    top_risk = make_top_risk_zones(df, args.bootstrap_iters, args.seed, args.top_n)

    # Add display-friendly columns while preserving raw numeric columns.
    overall_disp = add_percentage_columns(overall)
    by_domain_disp = add_percentage_columns(by_domain)
    by_condition_disp = add_percentage_columns(by_condition)
    by_dataset_disp = add_percentage_columns(by_dataset)
    by_dataset_condition_disp = add_percentage_columns(by_dataset_condition)
    top_risk_disp = add_percentage_columns(top_risk)

    save_table(overall_disp, out_dir / "table_overall_v2.csv")
    save_table(by_domain_disp, out_dir / "table_by_domain_v2.csv")
    save_table(by_condition_disp, out_dir / "table_by_condition_v2.csv")
    save_table(by_dataset_disp, out_dir / "table_by_dataset_v2.csv")
    save_table(by_dataset_condition_disp, out_dir / "table_by_dataset_condition_v2.csv")
    save_table(top_risk_disp, out_dir / "table_top_risk_zones_v2.csv")

    print("\nOverall:")
    print(
        overall[
            [
                "n",
                "silent_failure_rate",
                "citation_valid_wrong_rate",
                "abstention_failure_rate",
                "avg_correctness",
                "avg_confidence",
                "avg_danger_score",
            ]
        ].to_string(index=False)
    )

    print("\nBy domain:")
    print(
        by_domain[
            [
                "domain",
                "n",
                "silent_failure_rate",
                "citation_valid_wrong_rate",
                "abstention_failure_rate",
                "avg_correctness",
                "avg_danger_score",
            ]
        ].to_string(index=False)
    )

    print("\nBy condition:")
    print(
        by_condition[
            [
                "condition",
                "n",
                "silent_failure_rate",
                "citation_valid_wrong_rate",
                "abstention_failure_rate",
                "avg_correctness",
                "avg_danger_score",
            ]
        ].to_string(index=False)
    )

    print("\nTop risk zones:")
    print(top_risk.head(15).to_string(index=False))


if __name__ == "__main__":
    main()
