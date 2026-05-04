import argparse
from pathlib import Path

import pandas as pd


BOOL_COLS = [
    "silent_failure",
    "citation_valid_wrong",
    "abstention_failure",
    "nli_faithful",
    "nli_unfaithful",
    "nli_contradicted",
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


def clean_df(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    for col in BOOL_COLS:
        if col in df.columns:
            df[col] = ensure_bool(df[col])

    for col in ["nli_entailment", "nli_neutral", "nli_contradiction", "confidence", "correctness", "danger_score"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)

    return df


def summarize(df: pd.DataFrame, group_cols):
    agg_spec = dict(
        n=("instance_id", "count"),
        silent_failure_rate=("silent_failure", "mean"),
        citation_valid_wrong_rate=("citation_valid_wrong", "mean"),
        avg_entailment=("nli_entailment", "mean"),
        avg_neutral=("nli_neutral", "mean"),
        avg_contradiction=("nli_contradiction", "mean"),
        nli_faithful_rate=("nli_faithful", "mean"),
        nli_unfaithful_rate=("nli_unfaithful", "mean"),
        nli_contradicted_rate=("nli_contradicted", "mean"),
        avg_correctness=("correctness", "mean"),
        avg_confidence=("confidence", "mean"),
        avg_danger_score=("danger_score", "mean"),
    )

    if not group_cols:
        row = {
            "n": len(df),
            "silent_failure_rate": df["silent_failure"].mean(),
            "citation_valid_wrong_rate": df["citation_valid_wrong"].mean(),
            "avg_entailment": df["nli_entailment"].mean(),
            "avg_neutral": df["nli_neutral"].mean(),
            "avg_contradiction": df["nli_contradiction"].mean(),
            "nli_faithful_rate": df["nli_faithful"].mean(),
            "nli_unfaithful_rate": df["nli_unfaithful"].mean(),
            "nli_contradicted_rate": df["nli_contradicted"].mean(),
            "avg_correctness": df["correctness"].mean(),
            "avg_confidence": df["confidence"].mean(),
            "avg_danger_score": df["danger_score"].mean(),
        }
        return pd.DataFrame([row])

    return (
        df.groupby(group_cols, dropna=False)
        .agg(**agg_spec)
        .reset_index()
        .sort_values(["nli_unfaithful_rate", "silent_failure_rate"], ascending=False)
    )

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--faithfulness_csv", required=True)
    parser.add_argument("--out_dir", required=True)
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(args.faithfulness_csv)
    df = clean_df(df)

    overall = summarize(df, [])
    by_domain = summarize(df, ["domain"])
    by_condition = summarize(df, ["condition"])
    by_dataset_condition = summarize(df, ["domain", "dataset", "condition"])

    overall.to_csv(out_dir / "faithfulness_overall_v2.csv", index=False)
    by_domain.to_csv(out_dir / "faithfulness_by_domain_v2.csv", index=False)
    by_condition.to_csv(out_dir / "faithfulness_by_condition_v2.csv", index=False)
    by_dataset_condition.to_csv(out_dir / "faithfulness_by_dataset_condition_v2.csv", index=False)

    print("=" * 80)
    print("Citation faithfulness analysis v2")
    print("=" * 80)

    print("\nOverall:")
    print(overall.to_string(index=False))

    print("\nBy domain:")
    print(by_domain.to_string(index=False))

    print("\nBy condition:")
    print(by_condition.to_string(index=False))

    print("\nTop dataset-condition unfaithfulness:")
    print(by_dataset_condition.head(20).to_string(index=False))

    print("\nSaved:")
    print(out_dir / "faithfulness_overall_v2.csv")
    print(out_dir / "faithfulness_by_domain_v2.csv")
    print(out_dir / "faithfulness_by_condition_v2.csv")
    print(out_dir / "faithfulness_by_dataset_condition_v2.csv")


if __name__ == "__main__":
    main()
