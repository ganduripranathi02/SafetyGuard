# What changed

## Why the score was 30%
1. `evaluate.py` only counted replies containing "⚠️" / "I'm sorry" / "blocked" as blocked.
   Llama's refusals ("I can't provide…") were counted as failures.
2. The earlier "100%" was fake: API errors ("⚠️ Error calling model…") contain "⚠️".
3. The filter only knew injection phrases, nothing about harmful requests.

## Changes
- `safety_filter.py`: text normalisation (case, accents, leetspeak, zero-width chars, "b.o.m.b"),
  ~60 category rules (injection, weapons, violence, self-harm, cyber, fraud, drugs, crime, privacy…),
  a "defensive wording" override to reduce false positives, and an optional semantic layer
  (harmful + injection examples, thresholds configurable, loads lazily, never crashes if unavailable).
- `agent.py`: `run_agent()` returns a status (blocked / refused / answered / error); stronger system
  prompt; refusal detector; errors are never counted as blocks.
- `evaluate.py`: reports filter-blocked, model-refused, leaked, errors separately; `--no-llm` for
  free filter-only testing; `--benign` file to measure false positives.
- `test_openai.py`: uses OPENAI_MODEL (the hard-coded gpt-4o-mini caused the Ollama 404).
- `calibrate.py`: choose semantic thresholds from your own data.

## Run
    python evaluate.py adversarial_prompts.txt --benign benign_prompts.txt        # full pipeline
    python evaluate.py adversarial_prompts.txt --no-llm --benign benign_prompts.txt  # filter only
    python calibrate.py adversarial_prompts.txt benign_prompts.txt                # tune semantic layer
Set `SG_SEMANTIC=0` to skip the embedding model.
