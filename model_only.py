"""
Model-only baseline and over-refusal check.

Usage:
  python model_only.py unseen_harmful.txt unseen_benign.txt

For every prompt it asks the model directly (no filter), then combines that
reply with the filter decision, so ONE model call gives three views:
  model alone | filter alone | full pipeline (filter, then model)

Writes model_only_results.csv and prints a summary for the paper.
"""
import csv
import sys
import time

from agent import MODEL, SYSTEM_PROMPT, _client, is_refusal
from safety_filter import screen


def read(path):
    with open(path, encoding="utf-8") as f:
        return [l.strip() for l in f if l.strip()]


def ask_model(prompt):
    """Return (reply, error). Retries a few times on rate limits."""
    for _ in range(4):
        try:
            r = _client().chat.completions.create(
                model=MODEL,
                messages=[{"role": "system", "content": SYSTEM_PROMPT},
                          {"role": "user", "content": prompt}],
                max_tokens=200,
                temperature=0,
            )
            return (r.choices[0].message.content or "").strip(), None
        except Exception as e:
            err = str(e)
            if "429" in err:
                time.sleep(20)
                continue
            return "", err
    return "", err


def run(path, label):
    rows = []
    for i, p in enumerate(read(path), 1):
        d = screen(p)
        reply, err = ask_model(p)
        rows.append({
            "set": label, "prompt": p,
            "filter_blocked": d.blocked,
            "model_error": bool(err),
            "model_refused": (not err) and is_refusal(reply),
            "reply": (err or reply)[:300].replace("\n", " "),
        })
        print(f"[{label} {i}] filter={'BLOCK' if d.blocked else 'pass '} "
              f"model={'ERROR' if err else ('refuse' if rows[-1]['model_refused'] else 'answer')} | {p[:60]}")
        time.sleep(0.5)
    return rows


def pct(k, n):
    return f"{k}/{n} = {100 * k / n:.1f}%" if n else "n/a"


if __name__ == "__main__":
    harm_path, ben_path = sys.argv[1], sys.argv[2]
    harm = run(harm_path, "harmful")
    ben = run(ben_path, "benign")

    with open("model_only_results.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(harm[0].keys()))
        w.writeheader()
        w.writerows(harm + ben)

    hs = [r for r in harm if not r["model_error"]]
    bs = [r for r in ben if not r["model_error"]]
    n_h, n_b = len(hs), len(bs)
    print("\n" + "=" * 60)
    print(f"Model: {MODEL}   (errors excluded: harmful {len(harm) - n_h}, benign {len(ben) - n_b})")
    print("\nHARMFUL prompts (higher = safer)")
    print("  filter alone      :", pct(sum(r["filter_blocked"] for r in hs), n_h))
    print("  model alone       :", pct(sum(r["model_refused"] for r in hs), n_h))
    print("  full pipeline     :", pct(sum(r["filter_blocked"] or r["model_refused"] for r in hs), n_h))
    print("  leaked (pipeline) :", pct(sum(not (r["filter_blocked"] or r["model_refused"]) for r in hs), n_h))
    print("\nBENIGN prompts (lower = better)")
    print("  filter wrongly blocks   :", pct(sum(r["filter_blocked"] for r in bs), n_b))
    print("  model wrongly refuses   :", pct(sum(r["model_refused"] for r in bs), n_b))
    print("  pipeline wrongly stops  :", pct(sum(r["filter_blocked"] or r["model_refused"] for r in bs), n_b))
    print("\nBenign prompts the MODEL refused (check these by eye):")
    for r in bs:
        if r["model_refused"]:
            print("  -", r["prompt"], "|", r["reply"][:80])
    print("\nHarmful prompts the MODEL ALONE answered:")
    for r in hs:
        if not r["model_refused"]:
            print("  -", r["prompt"], "|", r["reply"][:80])
