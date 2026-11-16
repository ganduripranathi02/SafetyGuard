#!/bin/bash
# Runs: (1) unseen sets, (2) your own prompts, (3) semantic calibration, (4) report for slides.
# Usage:  bash run_all.sh            # full pipeline with Ollama (needs Ollama running)
#         NO_LLM=1 bash run_all.sh   # filter only, no Ollama needed
cd "$(dirname "$0")" || exit 1
export OPENAI_BASE_URL="${OPENAI_BASE_URL:-http://localhost:11434/v1}"
export OPENAI_API_KEY="${OPENAI_API_KEY:-ollama}"
export OPENAI_MODEL="${OPENAI_MODEL:-llama3.2}"
FLAG=""; [ "${NO_LLM:-0}" = "1" ] && FLAG="--no-llm"
mkdir -p results; rm -f results/*

run() {  # name harmful benign
  echo ">> $1"
  python evaluate.py "$2" $FLAG --benign "$3" > "results/$1.txt" 2>&1
  cp evaluation_result.csv "results/$1.csv"
  grep -E "Prompts:|blocked by filter|refused by model|LEAKED|errors|Safety score|Filter-only|False positives|wrongly" "results/$1.txt"
  echo
}

echo "=== STEP 1: unseen sets ==="
run original   adversarial_prompts.txt benign_prompts.txt
run fresh      fresh_harmful.txt       fresh_benign.txt
run held_out   held_out_harmful.txt    benign_prompts.txt

echo "=== STEP 2: your own prompts ==="
run my_test    my_test_harmful.txt     my_test_benign.txt

echo "=== STEP 3: semantic calibration ==="
cat adversarial_prompts.txt fresh_harmful.txt held_out_harmful.txt my_test_harmful.txt > results/all_harmful.txt
cat benign_prompts.txt fresh_benign.txt my_test_benign.txt > results/all_benign.txt
python calibrate.py results/all_harmful.txt results/all_benign.txt 2>&1 | grep -v -E "Warning|Loading|W1116|redirects" | tee results/calibrate.txt

echo "=== STEP 4: report for your presentation ==="
python make_report.py
echo "Done. Send me results/REPORT.md (and any LEAKED prompts listed in it)."
