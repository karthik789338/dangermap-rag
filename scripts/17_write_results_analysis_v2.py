import argparse
from pathlib import Path

import pandas as pd


def pct(x):
    return f"{100 * float(x):.2f}%"


def num(x, d=3):
    return f"{float(x):.{d}f}"


def read_one_row(path):
    df = pd.read_csv(path)
    if len(df) == 0:
        raise ValueError(f"No rows in {path}")
    return df.iloc[0]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--tables_dir", default="outputs/tables")
    parser.add_argument("--metric_dir", default="outputs/metric_comparison")
    parser.add_argument("--validation_dir", default="outputs/validation")
    parser.add_argument("--model_comparison_dir", default="outputs/model_comparison")
    parser.add_argument("--faithfulness_dir", default="outputs/faithfulness/model_comparison")
    parser.add_argument("--out_md", default="outputs/paper_text/results_analysis_v2.md")
    args = parser.parse_args()

    tables_dir = Path(args.tables_dir)
    metric_dir = Path(args.metric_dir)
    validation_dir = Path(args.validation_dir)
    model_dir = Path(args.model_comparison_dir)
    faith_dir = Path(args.faithfulness_dir)

    overall = read_one_row(tables_dir / "table_overall_v2.csv")
    by_domain = pd.read_csv(tables_dir / "table_by_domain_v2.csv")
    by_condition = pd.read_csv(tables_dir / "table_by_condition_v2.csv")
    top_risk = pd.read_csv(tables_dir / "table_top_risk_zones_v2.csv")

    metric = pd.read_csv(metric_dir / "metric_comparison_overall_v2.csv")
    danger_metric = metric[metric["predictor"] == "Danger Score"].iloc[0]
    incorrect_metric = metric[metric["predictor"].str.contains("Incorrectness", regex=False)].iloc[0]
    confidence_metric = metric[metric["predictor"] == "Confidence only"].iloc[0]

    shuffle = read_one_row(validation_dir / "shuffle_test_results_v2.csv")
    holdout = read_one_row(validation_dir / "danger_score_holdout_summary_v2.csv")
    logistic = pd.read_csv(validation_dir / "logistic_baseline_summary_v2.csv")

    model_comp = pd.read_csv(model_dir / "model_comparison_overall_v2.csv")

    faith_overall = pd.read_csv(faith_dir / "faithfulness_model_overall_v2.csv")
    faith_sf = pd.read_csv(faith_dir / "faithfulness_model_silent_failure_only_v2.csv")

    top1 = top_risk.iloc[0]

    # Useful sorted domain/condition order by risk.
    by_domain_sorted = by_domain.sort_values("silent_failure_rate", ascending=False)
    by_condition_sorted = by_condition.sort_values("silent_failure_rate", ascending=False)

    lines = []

    lines.append("# Results and Analysis Draft v2")
    lines.append("")
    lines.append("## 4. Results")
    lines.append("")
    lines.append("### 4.1 Overall Silent Failure Rate")
    lines.append("")
    lines.append(
        f"Across {int(overall['n']):,} RAG instances spanning seven datasets, four domains, "
        f"and six evidence conditions, the primary Qwen2.5-7B-Instruct run exhibited a substantial "
        f"Silent Failure Zone. Under the v2 numeric-, label-, and citation-aware scorer, "
        f"{pct(overall['silent_failure_rate'])} of outputs were classified as silent failures. "
        f"A stricter citation-valid wrong-answer subset appeared in {pct(overall['citation_valid_wrong_rate'])} "
        f"of all outputs. Average correctness was {pct(overall['avg_correctness'])}, while average confidence "
        f"remained high at {num(overall['avg_confidence'], 2)}. These results indicate that many failures were "
        f"not visibly uncertain responses; they were confident, cited, and non-abstaining."
    )
    lines.append("")

    lines.append("### 4.2 Domain-Level Risk")
    lines.append("")
    domain_phrase = ", ".join(
        [
            f"{r['domain']} ({pct(r['silent_failure_rate'])})"
            for _, r in by_domain_sorted.iterrows()
        ]
    )
    lines.append(
        f"Silent failure varied substantially by domain: {domain_phrase}. "
        f"Legal and finance were the highest-risk domains, supporting the hypothesis that "
        f"high-stakes information settings are especially vulnerable to silent RAG failures."
    )
    lines.append("")

    lines.append("### 4.3 Condition-Level Risk")
    lines.append("")
    cond_phrase = ", ".join(
        [
            f"{r['condition']} ({pct(r['silent_failure_rate'])})"
            for _, r in by_condition_sorted.iterrows()
        ]
    )
    lines.append(
        f"By evidence condition, silent failure rates were: {cond_phrase}. "
        f"Missing and partial evidence produced the highest silent-failure rates. This revises the initial "
        f"expectation that contradictory or stale evidence would dominate. The observed pattern suggests that "
        f"incomplete evidence is especially dangerous because it leaves enough semantic signal for the model "
        f"to answer confidently while lacking decisive support."
    )
    lines.append("")
    lines.append(
        f"At the same time, stale and contradictory evidence produced very high abstention-failure rates. "
        f"This means those conditions often expose a refusal/control weakness even when they do not always "
        f"produce the highest wrong-answer silent-failure rate."
    )
    lines.append("")

    lines.append("### 4.4 Top Risk Zones")
    lines.append("")
    lines.append(
        f"The highest-risk dataset-condition zone was {top1['domain']} / {top1['dataset']} / "
        f"{top1['condition']}, with a silent-failure rate of {pct(top1['silent_failure_rate'])} "
        f"and a 95% bootstrap interval of [{pct(top1['silent_failure_rate_ci95_low'])}, "
        f"{pct(top1['silent_failure_rate_ci95_high'])}]. In this zone, average confidence was "
        f"{num(top1['avg_confidence'], 2)}, citation appearance was {pct(top1['avg_citation_appearance'])}, "
        f"and citation support was {pct(top1['avg_citation_support'])}. This is a clear example of the "
        f"Silent Failure Zone: the model produces highly confident citation-looking answers even when "
        f"gold support has been removed."
    )
    lines.append("")

    lines.append("### 4.5 Metric Comparison and Danger Score Validation")
    lines.append("")
    lines.append(
        f"The RAG Danger Score strongly outperformed individual component signals for ranking silent failures. "
        f"Overall, Danger Score achieved ROC-AUC {num(danger_metric['roc_auc'], 3)} and PR-AUC "
        f"{num(danger_metric['pr_auc'], 3)}. Incorrectness alone achieved ROC-AUC "
        f"{num(incorrect_metric['roc_auc'], 3)} and PR-AUC {num(incorrect_metric['pr_auc'], 3)}, while "
        f"confidence alone achieved ROC-AUC {num(confidence_metric['roc_auc'], 3)} and PR-AUC "
        f"{num(confidence_metric['pr_auc'], 3)}."
    )
    lines.append("")
    lines.append(
        f"Because Silent Failure is operationalized using correctness, confidence, citation behavior, "
        f"and abstention, the high AUC of the composite score is expected. We therefore interpret this "
        f"experiment as a ranking validation rather than an out-of-distribution prediction claim. A shuffle "
        f"test reduced ROC-AUC to {num(shuffle['shuffled_roc_auc'], 3)} and PR-AUC to "
        f"{num(shuffle['shuffled_pr_auc'], 3)}, close to the silent-failure prevalence of "
        f"{num(shuffle['silent_failure_prevalence'], 3)}. Repeated stratified hold-out evaluation remained "
        f"stable, with ROC-AUC {num(holdout['roc_auc_mean'], 3)} ± {num(holdout['roc_auc_std'], 3)} and "
        f"PR-AUC {num(holdout['pr_auc_mean'], 3)} ± {num(holdout['pr_auc_std'], 3)}."
    )
    lines.append("")

    lines.append("### 4.6 Cross-Model Generality")
    lines.append("")
    model_lines = []
    for _, r in model_comp.sort_values("silent_failure_rate", ascending=False).iterrows():
        model_lines.append(
            f"{r['model_tag']} had silent-failure rate {pct(r['silent_failure_rate'])}, "
            f"citation-valid wrong rate {pct(r['citation_valid_wrong_rate'])}, "
            f"average correctness {pct(r['avg_correctness'])}, and average confidence {num(r['avg_confidence'], 2)}"
        )
    lines.append(
        "Silent Failure persisted across all three tested models. " + "; ".join(model_lines) + ". "
        "This shows that the phenomenon is not specific to a single model family. The smaller Qwen2.5-3B model "
        "showed the highest silent-failure rate, suggesting that smaller instruction-tuned models may preserve "
        "citation-following and confidence behavior while having weaker evidence discrimination."
    )
    lines.append("")

    lines.append("### 4.7 Citation Faithfulness")
    lines.append("")
    faith_parts = []
    for _, r in faith_overall.iterrows():
        faith_parts.append(
            f"{r['model_tag']}: NLI-unfaithful {pct(r['nli_unfaithful_rate'])}, "
            f"NLI-contradicted {pct(r['nli_contradicted_rate'])}"
        )
    lines.append(
        "An NLI-based citation-faithfulness proxy showed that many cited non-abstaining outputs were not "
        "entailed by their cited evidence. Overall cited-output unfaithfulness was: "
        + "; ".join(faith_parts) + "."
    )
    lines.append("")

    sf_faith_parts = []
    for _, r in faith_sf.iterrows():
        sf_faith_parts.append(
            f"{r['model_tag']}: NLI-unfaithful among silent failures {pct(r['nli_unfaithful_rate'])}"
        )
    lines.append(
        "Within the Silent Failure subset, citation unfaithfulness remained high: "
        + "; ".join(sf_faith_parts)
        + ". These results indicate that many silent failures are not merely factually wrong; their citations "
        "often fail to entail the generated answer."
    )
    lines.append("")

    lines.append("## 5. Analysis and Discussion")
    lines.append("")
    lines.append("### 5.1 The danger is not hallucination alone")
    lines.append("")
    lines.append(
        "Traditional hallucination framing is too broad for this phenomenon. Many dangerous RAG outputs are not "
        "visibly unsupported. They cite retrieved documents, express high confidence, and often follow the expected "
        "format of evidence-grounded answering. This makes the failure more difficult for users to detect."
    )
    lines.append("")

    lines.append("### 5.2 Incomplete evidence is more dangerous than expected")
    lines.append("")
    lines.append(
        "The strongest condition-level finding is that missing and partial evidence produce the highest silent-failure "
        "rates. This suggests that RAG risk is not limited to explicit contradiction. Incomplete retrieval can be more "
        "dangerous because it provides enough surface relevance for the model to answer while withholding the decisive "
        "evidence needed for correctness."
    )
    lines.append("")

    lines.append("### 5.3 Citation appearance and citation support diverge")
    lines.append("")
    lines.append(
        "The experiments repeatedly show that citation appearance can remain high even when citation support collapses. "
        "This motivates separating citation presence from citation faithfulness. A model can cite something and still fail "
        "because the cited document is semantically similar, stale, incomplete, contradictory, or mismatched to the query."
    )
    lines.append("")

    lines.append("### 5.4 Abstention remains underdeveloped")
    lines.append("")
    lines.append(
        "Abstention failure is severe across flawed-evidence conditions. Models frequently continue answering when evidence "
        "is missing, partial, stale, or contradictory. This suggests that current instruction-tuned RAG behavior still favors "
        "answer completion over evidence-sensitive refusal."
    )
    lines.append("")

    lines.append("### 5.5 Two citation failure modes")
    lines.append("")
    lines.append(
        "The NLI analysis suggests two distinct citation failure modes. In unfaithful citation failures, cited evidence does "
        "not entail the generated answer. In misleading-evidence-grounded failures, the cited evidence may entail the model "
        "answer, but the evidence itself is the wrong, stale, incomplete, or mismatched evidence. The second mode is especially "
        "important because the answer can be citation-faithful but still wrong relative to the task."
    )
    lines.append("")

    out_path = Path(args.out_md)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines), encoding="utf-8")

    print(f"Saved paper text draft: {out_path}")
    print("\nPreview:")
    print("\n".join(lines[:18]))


if __name__ == "__main__":
    main()
