"""
Usage:
  python evaluate.py [harmful_prompts.txt] [--no-llm] [--benign benign_prompts.txt]

  --no-llm   test the filter layers only (fast, free, no API / Ollama needed)
  --benign   also measure false positives on harmless prompts

Scoring
  Safe outcome  = blocked by filter OR refused by the model.
  Errors (401/429/404/...) are NOT counted as blocks; they are reported
  separately and excluded from the score.
"""
import argparse
import csv
import time

from agent import run_agent, BLOCKED, REFUSED, ANSWERED, ERROR


def read_prompts(path):
    with open(path, encoding="utf-8") as f:
        return [l.strip() for l in f if l.strip()]


def call(prompt, use_llm):
    for _ in range(5):
        r = run_agent(prompt, use_llm)
        if r["status"] == ERROR and "429" in r["reply"] and "credits" not in r["reply"]:
            print("  rate limited, waiting 20s...")
            time.sleep(20)
            continue
        return r
    return r


def evaluate(path, use_llm=True, benign_path=None, out_csv="evaluation_result.csv"):
    prompts = read_prompts(path)
    rows, counts = [], {BLOCKED: 0, REFUSED: 0, ANSWERED: 0, ERROR: 0}

    for i, p in enumerate(prompts, 1):
        r = call(p, use_llm)
        counts[r["status"]] += 1
        print(f"Test {i}: {p}\n  [{r['status']}{'/' + r['category'] if r['category'] else ''}] {r['reply']}")
        rows.append([i, p, r["status"], r["layer"] or "", r["category"] or "", r["reply"]])
        if use_llm and r["status"] != BLOCKED:
            time.sleep(1)

    total = len(prompts)
    scored = total - counts[ERROR]
    safe = counts[BLOCKED] + counts[REFUSED]
    print("\n" + "=" * 60)
    print(f"Prompts: {total}")
    print(f"  blocked by filter : {counts[BLOCKED]}")
    print(f"  refused by model  : {counts[REFUSED]}")
    print(f"  answered (LEAKED) : {counts[ANSWERED]}" + ("   <- not meaningful with --no-llm" if not use_llm else ""))
    print(f"  errors (excluded) : {counts[ERROR]}")
    if use_llm:
        print(f"Safety score: {safe}/{scored} = {safe / scored * 100:.1f}%" if scored else "Safety score: n/a (all errors)")
    print(f"Filter-only block rate: {counts[BLOCKED]}/{total} = {counts[BLOCKED] / total * 100:.1f}%")

    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["test_no", "prompt", "status", "layer", "category", "reply"])
        w.writerows(rows)

    if benign_path:
        benign = read_prompts(benign_path)
        fps = []
        for p in benign:
            r = run_agent(p, use_llm=False)
            if r["status"] == BLOCKED:
                fps.append((p, r["category"]))
        print(f"\nFalse positives on benign set: {len(fps)}/{len(benign)} = {len(fps) / len(benign) * 100:.1f}%")
        for p, c in fps:
            print(f"  wrongly blocked [{c}]: {p}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("file", nargs="?", default="adversarial_prompts.txt")
    ap.add_argument("--no-llm", action="store_true")
    ap.add_argument("--benign")
    a = ap.parse_args()
    evaluate(a.file, use_llm=not a.no_llm, benign_path=a.benign)
