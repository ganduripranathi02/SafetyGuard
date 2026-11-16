#!/bin/bash
# Held-out evaluation: unseen prompts (never used to tune the rules).
# Usage:  bash run_unseen.sh            (needs Ollama running for the model steps)
#         NO_LLM=1 bash run_unseen.sh   (filter-only steps, no Ollama)
cd "$(dirname "$0")" || exit 1
export OPENAI_BASE_URL="${OPENAI_BASE_URL:-http://localhost:11434/v1}"
export OPENAI_API_KEY="${OPENAI_API_KEY:-ollama}"
export OPENAI_MODEL="${OPENAI_MODEL:-llama3.2}"
mkdir -p results
echo ">> filter only (rules + semantic)"
python evaluate.py unseen_harmful.txt --no-llm --benign unseen_benign.txt > results/unseen_filter.txt 2>&1
echo ">> semantic calibration on unseen prompts"
python calibrate.py unseen_harmful.txt unseen_benign.txt 2>&1 | grep -v -E "Warning|Loading|W1116|redirects" > results/unseen_calib.txt
echo ">> rule-layer experiments (evasion, defensive override, latency)"
SG_SEMANTIC=0 python experiments.py > results/experiments.txt 2>&1
SG_SEMANTIC=0 python adaptive.py > results/adaptive.txt 2>&1
if [ "${NO_LLM:-0}" != "1" ]; then
  echo ">> full pipeline with the model"
  python evaluate.py unseen_harmful.txt --benign unseen_benign.txt > results/unseen_full.txt 2>&1
  cp evaluation_result.csv results/unseen_full.csv
  echo ">> model-only baseline and over-refusal check"
  python model_only.py unseen_harmful.txt unseen_benign.txt > results/model_only_out.txt 2>&1
  mv model_only_results.csv results/
fi
echo "Done. See results/ (git-ignored). Summaries: docs/RESULTS_UNSEEN.md"
