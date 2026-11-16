"""
Pick semantic-layer thresholds for YOUR data (needs sentence-transformers).

  python calibrate.py harmful.txt benign.txt

Prints, for each candidate threshold, how many harmful prompts would be caught
and how many benign prompts would be wrongly blocked by the semantic layer alone.
Use the lowest threshold with an acceptable false-positive count, then set
SG_INJECTION_THRESHOLD / SG_HARM_THRESHOLD (or edit safety_filter.py).
For a trustworthy choice use a few hundred prompts, e.g. the public AdvBench or
HarmBench harmful sets plus any benign instruction set (Alpaca, Dolly).
"""
import sys
import safety_filter as sf

def load(p):
    return [l.strip() for l in open(p, encoding="utf-8") if l.strip()]

harm, ben = load(sys.argv[1]), load(sys.argv[2])
def top(prompts):
    out = []
    for p in prompts:
        s = sf.semantic_scores(p)
        if s is None:
            sys.exit("semantic layer unavailable (install sentence-transformers / check network)")
        out.append(max(s))
    return out
h, b = top(harm), top(ben)
print("threshold  harmful_caught  benign_blocked")
for t in [x / 100 for x in range(40, 85, 5)]:
    print(f"  {t:.2f}     {sum(x > t for x in h):>4}/{len(h):<4}      {sum(x > t for x in b):>4}/{len(b)}")
