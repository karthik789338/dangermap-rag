#!/usr/bin/env bash
set -e

MODEL_ID="$1"
MODEL_TAG="$2"
LIMIT="$3"

if [ -z "$MODEL_ID" ] || [ -z "$MODEL_TAG" ] || [ -z "$LIMIT" ]; then
  echo "Usage: bash run/run_one_model_phase9.sh <model_id> <model_tag> <limit>"
  echo "Example: bash run/run_one_model_phase9.sh mistralai/Mistral-7B-Instruct-v0.3 mistral_7b 600"
  exit 1
fi

cd ~/dangermap-rag
source .venv/bin/activate

INPUT_INSTANCES="data/processed/dangermap_instances_12k_fever_finqa.jsonl"

OUT_RAW="outputs/${MODEL_TAG}_outputs.jsonl"
OUT_SCORED_JSONL="outputs/${MODEL_TAG}_scored_v2.jsonl"
OUT_SCORED_CSV="outputs/${MODEL_TAG}_scored_v2.csv"
OUT_SUMMARY="outputs/${MODEL_TAG}_summary_v2.csv"
OUT_TOP="outputs/${MODEL_TAG}_top_failures_v2.jsonl"

TABLE_DIR="outputs/tables_${MODEL_TAG}"
METRIC_DIR="outputs/metric_comparison_${MODEL_TAG}"
FIG_DIR="outputs/figures_${MODEL_TAG}"
VALID_DIR="outputs/validation_${MODEL_TAG}"

echo "============================================================"
echo "Running model: $MODEL_ID"
echo "Tag: $MODEL_TAG"
echo "Limit: $LIMIT"
echo "============================================================"

python scripts/04_run_llm_gpu.py \
  --input "$INPUT_INSTANCES" \
  --output "$OUT_RAW" \
  --model "$MODEL_ID" \
  --limit "$LIMIT" \
  --resume 2>&1 | tee "logs/${MODEL_TAG}_generation.log"

echo "============================================================"
echo "Scoring v2"
echo "============================================================"

python scripts/05b_score_outputs_v2.py \
  --instances "$INPUT_INSTANCES" \
  --input "$OUT_RAW" \
  --output_jsonl "$OUT_SCORED_JSONL" \
  --output_csv "$OUT_SCORED_CSV" 2>&1 | tee "logs/${MODEL_TAG}_score_v2.log"

echo "============================================================"
echo "Summarizing"
echo "============================================================"

python scripts/06_summarize_results.py \
  --scored_csv "$OUT_SCORED_CSV" \
  --summary_csv "$OUT_SUMMARY" \
  --top_failures "$OUT_TOP" 2>&1 | tee "logs/${MODEL_TAG}_summary_v2.log"

echo "============================================================"
echo "Paper tables"
echo "============================================================"

python scripts/07_make_paper_tables_v2.py \
  --input_csv "$OUT_SCORED_CSV" \
  --out_dir "$TABLE_DIR" \
  --bootstrap_iters 1000 \
  --top_n 25 2>&1 | tee "logs/${MODEL_TAG}_tables_v2.log"

echo "============================================================"
echo "Metric comparison"
echo "============================================================"

python scripts/09_metric_comparison_v2.py \
  --input_csv "$OUT_SCORED_CSV" \
  --out_dir "$METRIC_DIR" \
  --bootstrap_iters 1000 2>&1 | tee "logs/${MODEL_TAG}_metric_comparison_v2.log"

echo "============================================================"
echo "Metric figures"
echo "============================================================"

python scripts/08_make_all_paper_figures_v2.py \
  --scored_csv "$OUT_SCORED_CSV" \
  --top_risk_csv "${TABLE_DIR}/table_top_risk_zones_v2.csv" \
  --metric_csv "${METRIC_DIR}/metric_comparison_overall_v2.csv" \
  --out_dir "$FIG_DIR" 2>&1 | tee "logs/${MODEL_TAG}_figures_v2.log"

echo "============================================================"
echo "Validation sanity checks"
echo "============================================================"

python scripts/09b_validate_danger_score_v2.py \
  --input_csv "$OUT_SCORED_CSV" \
  --out_dir "$VALID_DIR" \
  --n_splits 10 \
  --test_size 0.33 2>&1 | tee "logs/${MODEL_TAG}_validation_v2.log"

echo "============================================================"
echo "Done: $MODEL_TAG"
echo "============================================================"
