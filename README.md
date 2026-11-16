# SafetyGuard

A small, layered input filter for LLM agents. It screens untrusted prompts for prompt injection and harmful requests **before** they reach the model.

> Companion code for the paper *Towards Robust AI: A Shield Against Evolving Threats* (Charitha, Pranathi, Sushmitha), Section X.
> This is a research prototype, not a production guardrail. Read [Known limitations](#known-limitations) first.

## How it works

```
prompt -> 1. normalise -> 2. rule layer -> 3. semantic layer (optional) -> 4. LLM + safety prompt + refusal detector
```

1. **Normalise:** Unicode decomposition, zero-width removal, lower-casing, leetspeak (`b0mb`), dotted words (`b.o.m.b`).
2. **Rule layer:** 82 regular expressions in 11 categories. 29 dual-use rules are suppressed when the prompt contains defensive or educational wording.
3. **Semantic layer (optional):** `all-MiniLM-L6-v2` cosine similarity to 26 exemplar sentences (threshold 0.70). Skipped if `sentence-transformers` is missing or `SG_SEMANTIC=0`.
4. **Model stage:** the prompt goes to an OpenAI-compatible endpoint (Llama 3.2 via Ollama in our runs) with a safety system prompt. A regex refusal detector labels the reply.

Each prompt ends as `blocked`, `refused`, `answered` or `error`. Errors are never counted as blocks.

## Quick start

```bash
pip install -r requirements.txt

# filter only (no model needed)
python evaluate.py adversarial_prompts.txt --no-llm --benign benign_prompts.txt

# full pipeline with a local model (Ollama running with llama3.2)
export OPENAI_BASE_URL=http://localhost:11434/v1 OPENAI_API_KEY=ollama OPENAI_MODEL=llama3.2
python evaluate.py adversarial_prompts.txt --benign benign_prompts.txt
```

Set `SG_SEMANTIC=0` to skip the embedding model.

## Reproducing the paper's results

| Script | What it does |
|---|---|
| `bash run_all.sh` | Development sets (rules were tuned on these), semantic calibration, report |
| `bash run_unseen.sh` | **Held-out** unseen prompts: filter, calibration, evasion, ablation, full pipeline, model-only baseline |
| `python model_only.py unseen_harmful.txt unseen_benign.txt` | Filter vs model vs pipeline, plus benign over-refusal |
| `python experiments.py` | Evasion robustness, defensive-override ablation, latency (rule layer) |
| `python adaptive.py` | Defensive-wording prefix bypass test |

Outputs go to `results/` (git-ignored; `run_all.sh` empties it each run). Committed summaries are in `RESULTS.md` and `docs/`.

## Results in brief

The 100% scores on the development sets measure **fit**, because the rules were adjusted on those prompts. The fair estimate is the unseen set (60 harmful, 60 benign, written after the rules were frozen):

| Configuration | Harmful stopped (n=60) | Benign wrongly stopped (n=60) |
|---|---|---|
| Rule layer alone | 34 (56.7%) | 4 (6.7%) |
| Filter (rules + semantic) | 35 (58.3%) | 4 (6.7%) |
| Llama 3.2 alone (safety prompt) | 57 (95.0%) | 9 (15.0%) |
| Full pipeline | 58 (96.7%) | 12 (20.0%) |

Full details: [`RESULTS.md`](RESULTS.md) and [`docs/RESULTS_UNSEEN.md`](docs/RESULTS_UNSEEN.md).

## Known limitations

- **Weak generalisation:** the rule layer caught 56.7% of unseen harmful prompts (95% CI 44.1-68.4%), against 100% on the tuned sets.
- **The filter adds little on top of this model:** Llama 3.2 alone stopped 95.0%; the filter adds one prompt (96.7%) and three extra wrongly stopped benign prompts.
- **Defensive-wording bypass:** prefixing a phrase such as `for awareness,` lets through all 55 of the 134 development prompts that depend only on suppressible rules.
- **Evasions not handled:** letter spacing (`m e t h`) and Cyrillic lookalike characters.
- **Jailbreak preambles:** the model agreed to drop its rules for 3 of 60 harmful prompts; the filter caught one.
- **Scope:** English, single-turn only, small sets, one model, refusals detected by phrase matching (partial refusals count as refusals). Indirect injection and multi-turn attacks are untested.

## Files

| Path | Purpose |
|---|---|
| `safety_filter.py` | Normalisation, rules, semantic layer, `screen()` |
| `agent.py` | Model call, system prompt, refusal detector, `run_agent()` |
| `evaluate.py` | Scores a prompt file (`--no-llm`, `--benign`) |
| `calibrate.py` | Semantic threshold sweep |
| `model_only.py` | Model-only baseline and over-refusal check |
| `experiments.py`, `adaptive.py` | Evasion, ablation, latency, bypass tests |
| `*_harmful.txt`, `*_benign.txt`, `adversarial_prompts.txt` | Prompt sets (requests only, no harmful answers) |
| `run_all.sh`, `run_unseen.sh`, `make_report.py` | Runners and report builder |

## Ethics

The prompt files contain requests for harmful content but no harmful answers. Do not use this as your only safety control.

## Licence

No licence has been chosen yet. Add one (for example MIT) before others reuse the code.
