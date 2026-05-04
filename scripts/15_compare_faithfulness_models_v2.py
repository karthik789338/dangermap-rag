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


def ensure_bool(s):
    if s.dtype == bool:
        return s
    return s.astype(str).str.lower().map({
        "true": True, "false": False, "1": True, "0": False,
        "yes": True, "no": False,
    }).fillna(False)


def load_csv(tag, path):
    df = pd.read_csv(path)
    df["model_tag"] = tag

    for col in BOOL_COLS:
        if col in df.columns:
            df[col] = ensure_bool(df[col])

    for col in ["nli_entailment", "nli_neutral", "nli_contradiction",
                "correctness", "confidence", "danger_score"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)

    return df


def summarize(df, group_cols):
    return (
        df.groupby(group_cols, dropna=False)
        .agg(
            n=("instance_id", "count"),
            silent_failure_rate=("silent_failure", "mean"),
            citation_valid_wrong_rate=("citation_valid_wrong", "mean"),
            nli_faithful_rate=("nli_faithful", "mean"),
            nli_unfaithful_rate=("nli_unfaithful", "mean"),
            nli_contradicted_rate=("nli_contradicted", "mean"),
            avg_entailment=("nli_entailment", "mean"),
            avg_neutral=("nli_neutral", "mean"),
            avg_contradiction=("nli_contradiction", "mean"),
            avg_correctness=("correctness", "mean"),
            avg_confidence=("confidence", "mean"),
            avg_danger_score=("danger_score", "mean"),
        )
        .reset_index()
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model_csv", action="append", required=True,
                        help="Format: model_tag=path/to/faithfulness.csv")
    parser.add_argument("--out_dir", default="outputs/faithfulness/model_comparison")
    args = parser.parse_args()

    frames = []
    for item in args.model_csv:
        tag, path = item.split("=", 1)
        frames.append(load_csv(tag, path))

    df = pd.concat(frames, ignore_index=True)

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    overall = summarize(df, ["model_tag"])
    by_domain = summarize(df, ["model_tag", "domain"])
    by_condition = summarize(df, ["model_tag", "condition"])
    sf_only = summarize(df[df["silent_failure"]], ["model_tag"])

    overall.to_csv(out_dir / "faithfulness_model_overall_v2.csv", index=False)
    by_domain.to_csv(out_dir / "faithfulness_model_by_domain_v2.csv", index=False)
    by_condition.to_csv(out_dir / "faithfulness_model_by_condition_v2.csv", index=False)
    sf_only.to_csv(out_dir / "faithfulness_model_silent_failure_only_v2.csv", index=False)

    print("=" * 80)
    print("Faithfulness model comparison")
    print("=" * 80)
    print("\nOverall:")
    print(overall.to_string(index=False))

    print("\nSilent-failure subset only:")
    print(sf_only.to_string(index=False))

    print("\nSaved to:", out_dir)


if __name__ == "__main__":
    main()
