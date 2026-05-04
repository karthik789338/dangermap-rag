import argparse
from pathlib import Path

import pandas as pd


def esc(x):
    s = str(x)
    repl = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    for k, v in repl.items():
        s = s.replace(k, v)
    return s


def pct(x):
    return f"{100 * float(x):.2f}\\%"


def num(x, d=3):
    return f"{float(x):.{d}f}"


def model_name(tag):
    mapping = {
        "qwen_7b": "Qwen2.5-7B-Instruct",
        "qwen_3b": "Qwen2.5-3B-Instruct",
        "mistral_7b": "Mistral-7B-Instruct-v0.3",
    }
    return mapping.get(str(tag), str(tag))


def read_one(path):
    df = pd.read_csv(path)
    if len(df) == 0:
        raise ValueError(f"Empty CSV: {path}")
    return df.iloc[0]


def table_benchmark_composition(df):
    lines = []
    lines.append(r"\begin{table*}[t]")
    lines.append(r"\centering")
    lines.append(r"\caption{Benchmark composition by domain and dataset. Each base item is transformed into six evidence conditions: clean, missing, partial, noisy, contradictory, and stale.}")
    lines.append(r"\label{tab:benchmark-composition}")
    lines.append(r"\begin{tabular}{llrr}")
    lines.append(r"\toprule")
    lines.append(r"Domain & Dataset & Base items & Perturbed instances \\")
    lines.append(r"\midrule")
    for _, r in df.iterrows():
        lines.append(
            f"{esc(r['domain'])} & {esc(r['dataset'])} & "
            f"{int(r['base_items'])} & {int(r['perturbed_instances'])} \\\\"
        )
    lines.append(r"\bottomrule")
    lines.append(r"\end{tabular}")
    lines.append(r"\end{table*}")
    return "\n".join(lines)


def table_domain_condition(domain_df, condition_df):
    lines = []
    lines.append(r"\begin{table*}[t]")
    lines.append(r"\centering")
    lines.append(r"\caption{Silent failure rates by domain and evidence condition for Qwen2.5-7B-Instruct under the v2 scorer.}")
    lines.append(r"\label{tab:domain-condition-risk}")
    lines.append(r"\begin{tabular}{lrrrr}")
    lines.append(r"\toprule")
    lines.append(r"Group & $n$ & Silent failure & Citation-valid wrong & Danger score \\")
    lines.append(r"\midrule")
    lines.append(r"\multicolumn{5}{l}{\textit{By domain}} \\")
    for _, r in domain_df.sort_values("silent_failure_rate", ascending=False).iterrows():
        lines.append(
            f"{esc(r['domain'])} & {int(r['n'])} & {pct(r['silent_failure_rate'])} & "
            f"{pct(r['citation_valid_wrong_rate'])} & {num(r['avg_danger_score'], 3)} \\\\"
        )
    lines.append(r"\midrule")
    lines.append(r"\multicolumn{5}{l}{\textit{By condition}} \\")
    for _, r in condition_df.sort_values("silent_failure_rate", ascending=False).iterrows():
        lines.append(
            f"{esc(r['condition'])} & {int(r['n'])} & {pct(r['silent_failure_rate'])} & "
            f"{pct(r['citation_valid_wrong_rate'])} & {num(r['avg_danger_score'], 3)} \\\\"
        )
    lines.append(r"\bottomrule")
    lines.append(r"\end{tabular}")
    lines.append(r"\end{table*}")
    return "\n".join(lines)


def table_top_risk(df, top_n=10):
    df = df.head(top_n)
    lines = []
    lines.append(r"\begin{table*}[t]")
    lines.append(r"\centering")
    lines.append(r"\caption{Top risk zones ranked by silent failure rate. Confidence intervals are 95\% bootstrap intervals.}")
    lines.append(r"\label{tab:top-risk-zones}")
    lines.append(r"\begin{tabular}{lllrrrr}")
    lines.append(r"\toprule")
    lines.append(r"Domain & Dataset & Condition & $n$ & Silent failure & 95\% CI & Citation support \\")
    lines.append(r"\midrule")
    for _, r in df.iterrows():
        ci = f"[{pct(r['silent_failure_rate_ci95_low'])}, {pct(r['silent_failure_rate_ci95_high'])}]"
        lines.append(
            f"{esc(r['domain'])} & {esc(r['dataset'])} & {esc(r['condition'])} & "
            f"{int(r['n'])} & {pct(r['silent_failure_rate'])} & {ci} & "
            f"{pct(r['avg_citation_support'])} \\\\"
        )
    lines.append(r"\bottomrule")
    lines.append(r"\end{tabular}")
    lines.append(r"\end{table*}")
    return "\n".join(lines)


def table_metric_comparison(df):
    lines = []
    lines.append(r"\begin{table*}[t]")
    lines.append(r"\centering")
    lines.append(r"\caption{Metric comparison for predicting the operationalized Silent Failure label. Higher values indicate better ranking.}")
    lines.append(r"\label{tab:metric-comparison}")
    lines.append(r"\begin{tabular}{lrr}")
    lines.append(r"\toprule")
    lines.append(r"Predictor & ROC-AUC & PR-AUC \\")
    lines.append(r"\midrule")
    for _, r in df.sort_values("roc_auc", ascending=False).iterrows():
        lines.append(
            f"{esc(r['predictor'])} & {num(r['roc_auc'], 3)} & {num(r['pr_auc'], 3)} \\\\"
        )
    lines.append(r"\bottomrule")
    lines.append(r"\end{tabular}")
    lines.append(r"\end{table*}")
    return "\n".join(lines)


def table_model_comparison(df):
    lines = []
    lines.append(r"\begin{table*}[t]")
    lines.append(r"\centering")
    lines.append(r"\caption{Cross-model comparison on the same 12,000-instance benchmark.}")
    lines.append(r"\label{tab:model-comparison}")
    lines.append(r"\begin{tabular}{lrrrrr}")
    lines.append(r"\toprule")
    lines.append(r"Model & Silent failure & Citation-valid wrong & Abstention failure & Correctness & Confidence \\")
    lines.append(r"\midrule")
    for _, r in df.sort_values("silent_failure_rate", ascending=False).iterrows():
        lines.append(
            f"{esc(model_name(r['model_tag']))} & {pct(r['silent_failure_rate'])} & "
            f"{pct(r['citation_valid_wrong_rate'])} & {pct(r['abstention_failure_rate'])} & "
            f"{pct(r['avg_correctness'])} & {num(r['avg_confidence'], 2)} \\\\"
        )
    lines.append(r"\bottomrule")
    lines.append(r"\end{tabular}")
    lines.append(r"\end{table*}")
    return "\n".join(lines)


def table_faithfulness(overall, sf):
    merged = overall.merge(
        sf[["model_tag", "nli_unfaithful_rate", "nli_contradicted_rate"]],
        on="model_tag",
        suffixes=("_overall", "_sf"),
    )
    lines = []
    lines.append(r"\begin{table*}[t]")
    lines.append(r"\centering")
    lines.append(r"\caption{NLI-based citation-faithfulness proxy across models. Overall rows include cited, non-abstaining outputs. Silent-failure rows restrict to outputs classified as Silent Failures.}")
    lines.append(r"\label{tab:citation-faithfulness}")
    lines.append(r"\begin{tabular}{lrrrr}")
    lines.append(r"\toprule")
    lines.append(r"Model & Overall unfaithful & Overall contradicted & SF unfaithful & SF contradicted \\")
    lines.append(r"\midrule")
    for _, r in merged.iterrows():
        lines.append(
            f"{esc(model_name(r['model_tag']))} & {pct(r['nli_unfaithful_rate_overall'])} & "
            f"{pct(r['nli_contradicted_rate_overall'])} & {pct(r['nli_unfaithful_rate_sf'])} & "
            f"{pct(r['nli_contradicted_rate_sf'])} \\\\"
        )
    lines.append(r"\bottomrule")
    lines.append(r"\end{tabular}")
    lines.append(r"\end{table*}")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--tables_dir", default="outputs/tables")
    parser.add_argument("--metric_dir", default="outputs/metric_comparison")
    parser.add_argument("--validation_dir", default="outputs/validation")
    parser.add_argument("--model_comparison_dir", default="outputs/model_comparison")
    parser.add_argument("--faithfulness_dir", default="outputs/faithfulness/model_comparison")
    parser.add_argument("--out_tex", default="outputs/paper_text/results_analysis_v2.tex")
    parser.add_argument("--out_tables_tex", default="outputs/paper_text/results_tables_v2.tex")
    args = parser.parse_args()

    tables_dir = Path(args.tables_dir)
    metric_dir = Path(args.metric_dir)
    validation_dir = Path(args.validation_dir)
    model_dir = Path(args.model_comparison_dir)
    faith_dir = Path(args.faithfulness_dir)

    overall = read_one(tables_dir / "table_overall_v2.csv")
    domain_df = pd.read_csv(tables_dir / "table_by_domain_v2.csv")
    condition_df = pd.read_csv(tables_dir / "table_by_condition_v2.csv")
    top_risk = pd.read_csv(tables_dir / "table_top_risk_zones_v2.csv")
    benchmark = pd.read_csv(tables_dir / "table_benchmark_composition_v2.csv")
    metric = pd.read_csv(metric_dir / "metric_comparison_overall_v2.csv")
    shuffle = read_one(validation_dir / "shuffle_test_results_v2.csv")
    holdout = read_one(validation_dir / "danger_score_holdout_summary_v2.csv")
    model_comp = pd.read_csv(model_dir / "model_comparison_overall_v2.csv")
    faith_overall = pd.read_csv(faith_dir / "faithfulness_model_overall_v2.csv")
    faith_sf = pd.read_csv(faith_dir / "faithfulness_model_silent_failure_only_v2.csv")

    danger_metric = metric[metric["predictor"] == "Danger Score"].iloc[0]
    incorrect_metric = metric[metric["predictor"].str.contains("Incorrectness", regex=False)].iloc[0]
    confidence_metric = metric[metric["predictor"] == "Confidence only"].iloc[0]

    domain_phrase = ", ".join(
        f"{r['domain']} ({pct(r['silent_failure_rate'])})"
        for _, r in domain_df.sort_values("silent_failure_rate", ascending=False).iterrows()
    )
    condition_phrase = ", ".join(
        f"{r['condition']} ({pct(r['silent_failure_rate'])})"
        for _, r in condition_df.sort_values("silent_failure_rate", ascending=False).iterrows()
    )

    top1 = top_risk.iloc[0]

    tex = []
    tex.append(r"\section{Results}")
    tex.append("")
    tex.append(r"\subsection{Overall silent failure rate}")
    tex.append(
        f"Across {int(overall['n']):,} RAG instances spanning seven datasets, four domains, "
        f"and six evidence conditions, Qwen2.5-7B-Instruct exhibited a substantial Silent Failure Zone. "
        f"Under the v2 numeric-, label-, and citation-aware scorer, {pct(overall['silent_failure_rate'])} "
        f"of outputs were classified as silent failures. A stricter citation-valid wrong-answer subset appeared in "
        f"{pct(overall['citation_valid_wrong_rate'])} of all outputs. Average correctness was "
        f"{pct(overall['avg_correctness'])}, while average confidence remained high at "
        f"{num(overall['avg_confidence'], 2)}. These results indicate that many failures were not visibly uncertain "
        f"responses; they were confident, cited, and non-abstaining."
    )
    tex.append("")
    tex.append(r"\subsection{Domain-level risk}")
    tex.append(
        f"Silent failure varied substantially by domain: {domain_phrase}. Legal and finance were the highest-risk "
        f"domains, supporting the hypothesis that high-stakes information settings are especially vulnerable to "
        f"silent RAG failures."
    )
    tex.append("")
    tex.append(r"\subsection{Condition-level risk}")
    tex.append(
        f"By evidence condition, silent failure rates were: {condition_phrase}. Missing and partial evidence produced "
        f"the highest silent-failure rates. This revises the initial expectation that contradictory or stale evidence "
        f"would dominate. The observed pattern suggests that incomplete evidence is especially dangerous because it "
        f"leaves enough semantic signal for the model to answer confidently while lacking decisive support."
    )
    tex.append(
        "At the same time, stale and contradictory evidence produced very high abstention-failure rates. "
        "This means those conditions often expose a refusal-control weakness even when they do not always produce "
        "the highest wrong-answer silent-failure rate."
    )
    tex.append("")
    tex.append(r"\subsection{Top risk zones}")
    tex.append(
        f"The highest-risk dataset-condition zone was {esc(top1['domain'])}/{esc(top1['dataset'])}/"
        f"{esc(top1['condition'])}, with a silent-failure rate of {pct(top1['silent_failure_rate'])} "
        f"and a 95\\% bootstrap interval of [{pct(top1['silent_failure_rate_ci95_low'])}, "
        f"{pct(top1['silent_failure_rate_ci95_high'])}]. In this zone, average confidence was "
        f"{num(top1['avg_confidence'], 2)}, citation appearance was {pct(top1['avg_citation_appearance'])}, "
        f"and citation support was {pct(top1['avg_citation_support'])}. This is a clear example of the Silent "
        f"Failure Zone: the model produces highly confident citation-looking answers even when gold support has "
        f"been removed."
    )
    tex.append("")
    tex.append(r"\subsection{Metric comparison and Danger Score validation}")
    tex.append(
        f"The RAG Danger Score strongly outperformed individual component signals for ranking silent failures. "
        f"Overall, Danger Score achieved ROC-AUC {num(danger_metric['roc_auc'], 3)} and PR-AUC "
        f"{num(danger_metric['pr_auc'], 3)}. Incorrectness alone achieved ROC-AUC "
        f"{num(incorrect_metric['roc_auc'], 3)} and PR-AUC {num(incorrect_metric['pr_auc'], 3)}, while "
        f"confidence alone achieved ROC-AUC {num(confidence_metric['roc_auc'], 3)} and PR-AUC "
        f"{num(confidence_metric['pr_auc'], 3)}."
    )
    tex.append(
        f"Because Silent Failure is operationalized using correctness, confidence, citation behavior, and abstention, "
        f"the high AUC of the composite score is expected. We therefore interpret this experiment as a ranking "
        f"validation rather than an out-of-distribution prediction claim. A shuffle test reduced ROC-AUC to "
        f"{num(shuffle['shuffled_roc_auc'], 3)} and PR-AUC to {num(shuffle['shuffled_pr_auc'], 3)}, close to "
        f"the silent-failure prevalence of {num(shuffle['silent_failure_prevalence'], 3)}. Repeated stratified "
        f"hold-out evaluation remained stable, with ROC-AUC {num(holdout['roc_auc_mean'], 3)} $\\pm$ "
        f"{num(holdout['roc_auc_std'], 3)} and PR-AUC {num(holdout['pr_auc_mean'], 3)} $\\pm$ "
        f"{num(holdout['pr_auc_std'], 3)}."
    )
    tex.append("")
    tex.append(r"\subsection{Cross-model generality}")
    model_bits = []
    for _, r in model_comp.sort_values("silent_failure_rate", ascending=False).iterrows():
        model_bits.append(
            f"{esc(model_name(r['model_tag']))} had silent-failure rate {pct(r['silent_failure_rate'])}, "
            f"citation-valid wrong rate {pct(r['citation_valid_wrong_rate'])}, average correctness "
            f"{pct(r['avg_correctness'])}, and average confidence {num(r['avg_confidence'], 2)}"
        )
    tex.append(
        "Silent Failure persisted across all three tested models. "
        + "; ".join(model_bits)
        + ". This shows that the phenomenon is not specific to a single model family. The smaller Qwen2.5-3B "
        + "model showed the highest silent-failure rate, suggesting that smaller instruction-tuned models may "
        + "preserve citation-following and confidence behavior while having weaker evidence discrimination."
    )
    tex.append("")
    tex.append(r"\subsection{Citation faithfulness}")
    faith_bits = []
    for _, r in faith_overall.iterrows():
        faith_bits.append(
            f"{esc(model_name(r['model_tag']))}: NLI-unfaithful {pct(r['nli_unfaithful_rate'])}, "
            f"NLI-contradicted {pct(r['nli_contradicted_rate'])}"
        )
    tex.append(
        "An NLI-based citation-faithfulness proxy showed that many cited non-abstaining outputs were not entailed "
        "by their cited evidence. Overall cited-output unfaithfulness was: "
        + "; ".join(faith_bits)
        + "."
    )
    sf_bits = []
    for _, r in faith_sf.iterrows():
        sf_bits.append(
            f"{esc(model_name(r['model_tag']))}: NLI-unfaithful among silent failures {pct(r['nli_unfaithful_rate'])}"
        )
    tex.append(
        "Within the Silent Failure subset, citation unfaithfulness remained high: "
        + "; ".join(sf_bits)
        + ". These results indicate that many silent failures are not merely factually wrong; their citations often "
        + "fail to entail the generated answer."
    )
    tex.append("")
    tex.append(r"\section{Analysis and Discussion}")
    tex.append("")
    tex.append(r"\subsection{The danger is not hallucination alone}")
    tex.append(
        "Traditional hallucination framing is too broad for this phenomenon. Many dangerous RAG outputs are not visibly "
        "unsupported. They cite retrieved documents, express high confidence, and often follow the expected format of "
        "evidence-grounded answering. This makes the failure more difficult for users to detect."
    )
    tex.append("")
    tex.append(r"\subsection{Incomplete evidence is more dangerous than expected}")
    tex.append(
        "The strongest condition-level finding is that missing and partial evidence produce the highest silent-failure "
        "rates. This suggests that RAG risk is not limited to explicit contradiction. Incomplete retrieval can be more "
        "dangerous because it provides enough surface relevance for the model to answer while withholding the decisive "
        "evidence needed for correctness."
    )
    tex.append("")
    tex.append(r"\subsection{Citation appearance and citation support diverge}")
    tex.append(
        "The experiments repeatedly show that citation appearance can remain high even when citation support collapses. "
        "This motivates separating citation presence from citation faithfulness. A model can cite something and still "
        "fail because the cited document is semantically similar, stale, incomplete, contradictory, or mismatched to the query."
    )
    tex.append("")
    tex.append(r"\subsection{Abstention remains underdeveloped}")
    tex.append(
        "Abstention failure is severe across flawed-evidence conditions. Models frequently continue answering when evidence "
        "is missing, partial, stale, or contradictory. This suggests that current instruction-tuned RAG behavior still favors "
        "answer completion over evidence-sensitive refusal."
    )
    tex.append("")
    tex.append(r"\subsection{Two citation failure modes}")
    tex.append(
        "The NLI analysis suggests two distinct citation failure modes. In unfaithful citation failures, cited evidence does "
        "not entail the generated answer. In misleading-evidence-grounded failures, the cited evidence may entail the model "
        "answer, but the evidence itself is the wrong, stale, incomplete, or mismatched evidence. The second mode is especially "
        "important because the answer can be citation-faithful but still wrong relative to the task."
    )

    tables = []
    tables.append(table_benchmark_composition(benchmark))
    tables.append(table_domain_condition(domain_df, condition_df))
    tables.append(table_top_risk(top_risk, top_n=10))
    tables.append(table_metric_comparison(metric))
    tables.append(table_model_comparison(model_comp))
    tables.append(table_faithfulness(faith_overall, faith_sf))

    out_tex = Path(args.out_tex)
    out_tables = Path(args.out_tables_tex)
    out_tex.parent.mkdir(parents=True, exist_ok=True)
    out_tables.parent.mkdir(parents=True, exist_ok=True)
    out_tex.write_text("\n\n".join(tex), encoding="utf-8")
    out_tables.write_text("\n\n".join(tables), encoding="utf-8")

    print(f"Saved LaTeX results text: {out_tex}")
    print(f"Saved LaTeX tables: {out_tables}")


if __name__ == "__main__":
    main()
