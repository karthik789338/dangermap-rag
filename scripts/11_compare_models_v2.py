import argparse
from pathlib import Path

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


def load_model_csv(path: str, model_tag: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    df["model_tag"] = model_tag

    for col in BOOL_COLS:
        if col in df.columns:
            df[col] = ensure_bool(df[col])

    numeric_cols = [
        "correctness",
        "confidence",
        "danger_score",
        "citation_appearance",
        "citation_support_proxy",
    ]

    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)

    return df


def summarize(df: pd.DataFrame, group_cols):
    return (
        df.groupby(group_cols, dropna=False)
        .agg(
            n=("instance_id", "count"),
            silent_failure_rate=("silent_failure", "mean"),
            citation_valid_wrong_rate=("citation_valid_wrong", "mean"),
            abstention_failure_rate=("abstention_failure", "mean"),
            avg_correctness=("correctness", "mean"),
            avg_confidence=("confidence", "mean"),
            avg_danger_score=("danger_score", "mean"),
            avg_citation_appearance=("citation_appearance", "mean"),
            avg_citation_support=("citation_support_proxy", "mean"),
        )
        .reset_index()
        .sort_values(group_cols)
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--model_csv",
        action="append",
        required=True,
        help="Format: model_tag=path/to/scored.csv",
    )
    parser.add_argument(
        "--out_dir",
        default="outputs/model_comparison",
    )
    args = parser.parse_args()

    frames = []

    for item in args.model_csv:
        if "=" not in item:
            raise ValueError("Each --model_csv must be formatted model_tag=path.csv")

        tag, path = item.split("=", 1)
        frames.append(load_model_csv(path, tag))

    df = pd.concat(frames, ignore_index=True)

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    overall = summarize(df, ["model_tag"])
    by_domain = summarize(df, ["model_tag", "domain"])
    by_condition = summarize(df, ["model_tag", "condition"])
    by_domain_condition = summarize(df, ["model_tag", "domain", "condition"])

    overall.to_csv(out_dir / "model_comparison_overall_v2.csv", index=False)
    by_domain.to_csv(out_dir / "model_comparison_by_domain_v2.csv", index=False)
    by_condition.to_csv(out_dir / "model_comparison_by_condition_v2.csv", index=False)
    by_domain_condition.to_csv(out_dir / "model_comparison_by_domain_condition_v2.csv", index=False)

    print("=" * 80)
    print("Model comparison overall")
    print("=" * 80)
    print(overall.to_string(index=False))

    print("\nSaved:")
    print(out_dir / "model_comparison_overall_v2.csv")
    print(out_dir / "model_comparison_by_domain_v2.csv")
    print(out_dir / "model_comparison_by_condition_v2.csv")
    print(out_dir / "model_comparison_by_domain_condition_v2.csv")


if __name__ == "__main__":
    main()
