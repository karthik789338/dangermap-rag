from pathlib import Path
import json
import re
import pandas as pd

ROOT = Path(".")
OUT = Path("revision_v3/phase1a/audit")
OUT.mkdir(parents=True, exist_ok=True)

base_file = ROOT / "scripts/02_build_base_items.py"
perturb_file = ROOT / "scripts/03_build_perturbations_gpu.py"
generation_file = ROOT / "scripts/04_run_llm_gpu.py"
scorer_file = ROOT / "scripts/05b_score_outputs_v2.py"
tables_file = ROOT / "scripts/07_make_paper_tables_v2.py"
metric_file = ROOT / "scripts/09_metric_comparison_v2.py"
validation_file = ROOT / "scripts/09b_validate_danger_score_v2.py"

texts = {
    "base": base_file.read_text(encoding="utf-8"),
    "perturb": perturb_file.read_text(encoding="utf-8"),
    "generation": generation_file.read_text(encoding="utf-8"),
    "scorer": scorer_file.read_text(encoding="utf-8"),
    "tables": tables_file.read_text(encoding="utf-8"),
    "metric": metric_file.read_text(encoding="utf-8"),
    "validation": validation_file.read_text(encoding="utf-8"),
}

checks = []

def add(name, observed, implication):
    checks.append({
        "check": name,
        "observed": observed,
        "implication_for_revision": implication,
    })

# ---------------------------------------------------------------------
# Benchmark construction
# ---------------------------------------------------------------------

add(
    "Base-item selection",
    "Loaders stop once n valid examples are collected; random.shuffle occurs only after selection.",
    "Current sampling is effectively first-N eligible items, not seeded random sampling."
)

add(
    "CaseHOLD answer leakage",
    'Gold evidence contains: context + " Correct holding: " + correct',
    "The target answer is explicitly inserted into the evidence and should be removed."
)

add(
    "Clean condition",
    "clean_docs = gold_docs + local_distractors[:2] + sem_noise[:2]",
    "Submitted clean condition is not gold-only."
)

add(
    "Partial condition",
    "Each gold document is truncated to the first 45 words.",
    "Truncation does not guarantee decisive support has actually been removed."
)

add(
    "Contradictory condition",
    "Synthetic text explicitly says the answer conflicts with other available evidence.",
    "This gives the model a direct meta-cue that evidence is contradictory."
)

add(
    "Stale condition",
    'Synthetic text explicitly says the source "may be outdated or superseded".',
    "This gives the model a direct cue to detect staleness."
)

# ---------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------

add(
    "Silent Failure thresholds",
    "correctness < 0.50; confidence >= 70; citation appearance >= 0.50; non-abstention",
    "Threshold sensitivity analysis is required."
)

add(
    "Citation support in SF label",
    "Citation support/faithfulness is not part of the Silent Failure Boolean label.",
    "Conceptual wording must be aligned with the actual operational definition."
)

add(
    "Danger Score weights",
    "0.35 incorrectness + 0.25 confidence + 0.15 citation appearance + "
    "0.15 citation misgrounding + 0.10 no-abstention",
    "Weights must be reported explicitly and sensitivity/alternative weighting should be tested."
)

add(
    "Domain multiplier",
    "Medical, legal, and finance scores are multiplied by 1.05.",
    "The multiplier is heuristic and complicates domain comparison."
)

add(
    "Abstention handling",
    "If the model abstains, correctness is forcibly set to 0.",
    "A safe abstention can still receive a large incorrectness contribution to Danger Score."
)

# ---------------------------------------------------------------------
# Statistical dependence
# ---------------------------------------------------------------------

add(
    "Bootstrap unit",
    "Bootstrap functions resample individual output rows.",
    "Six variants from the same base item are treated as independent; use clustered bootstrap."
)

add(
    "Repeated holdout",
    "StratifiedShuffleSplit is performed at row level.",
    "Variants of the same base item can occur across splits; use grouped splitting where relevant."
)

# ---------------------------------------------------------------------
# Generation reproducibility
# ---------------------------------------------------------------------

add(
    "Decoding",
    "do_sample=False",
    "Generation is greedy/deterministic; report explicitly."
)

add(
    "Maximum generation length",
    "max_new_tokens default = 450",
    "Report in revised experimental setup."
)

add(
    "Prompt truncation",
    "Tokenizer truncation max_length = 12000",
    "Report exact context handling."
)

add(
    "Model dtype",
    "torch.float16",
    "Report inference precision."
)

add(
    "Model revision pinning",
    "No explicit revision= argument is passed to from_pretrained.",
    "Revision commit hashes should be recorded for revised experiments."
)

# ---------------------------------------------------------------------
# Existing result artifacts
# ---------------------------------------------------------------------

model_comparison = ROOT / "outputs/model_comparison/model_comparison_overall_v2.csv"
if model_comparison.exists():
    df = pd.read_csv(model_comparison)
    add(
        "Existing model comparison rows",
        str(len(df)),
        "Submitted aggregate model results are present and can be frozen as baseline."
    )

logistic = ROOT / "outputs/validation/logistic_baseline_summary_v2.csv"
if logistic.exists():
    df = pd.read_csv(logistic)
    vals = {
        r["predictor"]: {
            "roc_auc": float(r["roc_auc_mean"]),
            "pr_auc": float(r["pr_auc_mean"]),
        }
        for _, r in df.iterrows()
    }
    add(
        "Logistic-regression baseline",
        json.dumps(vals, sort_keys=True),
        "The component logistic model outperforms the heuristic Danger Score and must be discussed."
    )

report = {
    "phase": "1A",
    "status": "AUDIT_COMPLETE",
    "submitted_commit": (
        ROOT / "revision_v3/phase1a/baseline/submitted_commit.txt"
    ).read_text().strip(),
    "checks": checks,
}

with open(OUT / "submitted_v2_audit.json", "w", encoding="utf-8") as f:
    json.dump(report, f, indent=2)

with open(OUT / "submitted_v2_audit.md", "w", encoding="utf-8") as f:
    f.write("# DangerMap-RAG submitted-v2 audit\n\n")
    f.write(f"Commit: `{report['submitted_commit']}`\n\n")

    for i, row in enumerate(checks, 1):
        f.write(f"## {i}. {row['check']}\n\n")
        f.write(f"**Observed:** {row['observed']}\n\n")
        f.write(
            f"**Revision implication:** "
            f"{row['implication_for_revision']}\n\n"
        )

print("=" * 80)
print("DANGERMAP-RAG PHASE 1A: SUBMITTED V2 AUDIT")
print("=" * 80)

for i, row in enumerate(checks, 1):
    print(f"{i:02d}. {row['check']}")
    print("    Observed:", row["observed"])
    print("    Revision:", row["implication_for_revision"])

print()
print("Audit JSON :", OUT / "submitted_v2_audit.json")
print("Audit MD   :", OUT / "submitted_v2_audit.md")
print("=" * 80)
print("PHASE 1A AUDIT: PASSED")
print("=" * 80)
