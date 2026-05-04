import argparse
import json
from pathlib import Path

import pandas as pd


def write_jsonl(path, rows):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--scored_csv", default="outputs/qwen_7b_dangermap_12k_scored.csv")
    parser.add_argument("--summary_csv", default="outputs/qwen_7b_dangermap_12k_summary.csv")
    parser.add_argument("--top_failures", default="outputs/qwen_7b_top_silent_failures.jsonl")
    parser.add_argument("--top_n", type=int, default=100)
    args = parser.parse_args()

    df = pd.read_csv(args.scored_csv)

    if len(df) == 0:
        print("No rows found.")
        return

    summary = (
        df.groupby(["domain", "dataset", "condition"], dropna=False)
        .agg(
            n=("instance_id", "count"),
            avg_correctness=("correctness", "mean"),
            avg_confidence=("confidence", "mean"),
            avg_citation_appearance=("citation_appearance", "mean"),
            avg_citation_support_proxy=("citation_support_proxy", "mean"),
            abstention_rate=("model_abstain", "mean"),
            abstention_failure_rate=("abstention_failure", "mean"),
            silent_failure_rate=("silent_failure", "mean"),
            avg_danger_score=("danger_score", "mean"),
        )
        .reset_index()
        .sort_values(["silent_failure_rate", "avg_danger_score"], ascending=False)
    )

    Path(args.summary_csv).parent.mkdir(parents=True, exist_ok=True)
    summary.to_csv(args.summary_csv, index=False)

    print("\nSaved summary:", args.summary_csv)
    print("\nTop summary rows:")
    print(summary.head(30).to_string(index=False))

    top = (
        df.sort_values(["silent_failure", "danger_score", "confidence"], ascending=False)
        .head(args.top_n)
        .to_dict(orient="records")
    )

    write_jsonl(args.top_failures, top)
    print("\nSaved top failures:", args.top_failures)


if __name__ == "__main__":
    main()
