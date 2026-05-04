import argparse
import json
from pathlib import Path
from collections import Counter

import pandas as pd


def read_jsonl(path):
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def save(df, path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
    print(f"Saved: {path} ({len(df)} rows)")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--base_items",
        default="data/processed/base_items_2k_fever_finqa.jsonl",
    )
    parser.add_argument(
        "--instances",
        default="data/processed/dangermap_instances_12k_fever_finqa.jsonl",
    )
    parser.add_argument(
        "--out_dir",
        default="outputs/tables",
    )
    args = parser.parse_args()

    out_dir = Path(args.out_dir)

    base = read_jsonl(args.base_items)
    inst = read_jsonl(args.instances)

    print("=" * 80)
    print("Benchmark appendix table builder v2")
    print("=" * 80)
    print("Base items:", len(base))
    print("Perturbed instances:", len(inst))

    base_df = pd.DataFrame(
        [
            {
                "base_id": r.get("base_id"),
                "domain": r.get("domain"),
                "dataset": r.get("dataset"),
                "task_type": r.get("task_type"),
            }
            for r in base
        ]
    )

    inst_df = pd.DataFrame(
        [
            {
                "instance_id": r.get("instance_id"),
                "base_id": r.get("base_id"),
                "domain": r.get("domain"),
                "dataset": r.get("dataset"),
                "task_type": r.get("task_type"),
                "condition": r.get("condition"),
                "should_abstain": r.get("should_abstain"),
                "perturbation_source": r.get("perturbation_source"),
            }
            for r in inst
        ]
    )

    table_composition = (
        base_df.groupby(["domain", "dataset", "task_type"], dropna=False)
        .agg(base_items=("base_id", "count"))
        .reset_index()
        .sort_values(["domain", "dataset", "task_type"])
    )

    instance_counts = (
        inst_df.groupby(["domain", "dataset", "task_type"], dropna=False)
        .agg(perturbed_instances=("instance_id", "count"))
        .reset_index()
    )

    table_composition = table_composition.merge(
        instance_counts,
        on=["domain", "dataset", "task_type"],
        how="left",
    )

    table_composition["conditions_per_base_item"] = (
        table_composition["perturbed_instances"] / table_composition["base_items"]
    )

    table_condition_counts = (
        inst_df.groupby(["domain", "dataset", "condition"], dropna=False)
        .agg(
            instances=("instance_id", "count"),
            expected_abstention_rate=("should_abstain", "mean"),
        )
        .reset_index()
        .sort_values(["domain", "dataset", "condition"])
    )

    table_domain_totals = (
        inst_df.groupby(["domain"], dropna=False)
        .agg(
            perturbed_instances=("instance_id", "count"),
            base_items=("base_id", "nunique"),
        )
        .reset_index()
        .sort_values("domain")
    )

    table_condition_totals = (
        inst_df.groupby(["condition"], dropna=False)
        .agg(
            perturbed_instances=("instance_id", "count"),
            base_items=("base_id", "nunique"),
            expected_abstention_rate=("should_abstain", "mean"),
        )
        .reset_index()
        .sort_values("condition")
    )

    save(table_composition, out_dir / "table_benchmark_composition_v2.csv")
    save(table_condition_counts, out_dir / "table_benchmark_condition_counts_v2.csv")
    save(table_domain_totals, out_dir / "table_benchmark_domain_totals_v2.csv")
    save(table_condition_totals, out_dir / "table_benchmark_condition_totals_v2.csv")

    print("\nBenchmark composition:")
    print(table_composition.to_string(index=False))

    print("\nDomain totals:")
    print(table_domain_totals.to_string(index=False))

    print("\nCondition totals:")
    print(table_condition_totals.to_string(index=False))


if __name__ == "__main__":
    main()
