"""Builds results/REPORT.md (table for your slides + list of leaked / wrongly-blocked prompts)."""
import csv, re, os

SETS = [("original", "Original 49 (rules tuned on these)"),
        ("held_out", "Held-out 30 (partly tuned)"),
        ("fresh", "Fresh 25 (partly tuned)"),
        ("my_test", "My own 30 (63% before tuning, then tuned)")]

def read(name):
    p = f"results/{name}.csv"
    if not os.path.exists(p):
        return None
    with open(p, encoding="utf-8") as f:
        return list(csv.DictReader(f))

lines = ["# SafetyGuard results\n",
         "| Test set | Prompts | Filter blocked | Model refused | Leaked | Errors | Safety score | False positives |",
         "|---|---|---|---|---|---|---|---|"]
leaks = []
for key, label in SETS:
    rows = read(key)
    if rows is None:
        continue
    c = {s: sum(r["status"] == s for r in rows) for s in
         ["blocked_by_filter", "refused_by_model", "answered", "error"]}
    n = len(rows); scored = n - c["error"]
    safe = c["blocked_by_filter"] + c["refused_by_model"]
    txt = open(f"results/{key}.txt", encoding="utf-8").read()
    fp = re.search(r"False positives on benign set: (\d+/\d+)", txt)
    score = f"{safe}/{scored} = {safe / scored * 100:.1f}%" if scored else "n/a"
    lines.append(f"| {label} | {n} | {c['blocked_by_filter']} | {c['refused_by_model']} | "
                 f"{c['answered']} | {c['error']} | {score} | {fp.group(1) if fp else 'n/a'} |")
    leaks += [(key, r["prompt"]) for r in rows if r["status"] == "answered"]
    for m in re.findall(r"wrongly blocked \[(.*?)\]: (.*)", txt):
        leaks.append((key + " (FALSE POSITIVE)", m[1]))

lines.append("\n## Prompts to fix (leaked or wrongly blocked)\n")
lines += [f"- [{k}] {p}" for k, p in leaks] or ["- none"]
if os.path.exists("results/calibrate.txt"):
    lines.append("\n## Semantic threshold calibration\n```")
    lines.append(open("results/calibrate.txt", encoding="utf-8").read().strip())
    lines.append("```")
open("results/REPORT.md", "w", encoding="utf-8").write("\n".join(lines) + "\n")
print("\n".join(lines))
