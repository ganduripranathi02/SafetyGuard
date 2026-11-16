import os; os.environ["SG_SEMANTIC"]="0"
import safety_filter as sf, math
L=lambda p:[l.strip() for l in open(p,encoding='utf-8') if l.strip()]
h=L('adversarial_prompts.txt')+L('held_out_harmful.txt')+L('fresh_harmful.txt')+L('my_test_harmful.txt')
caught=[p for p in h if sf.rule_filter(p)]
defens=[r for r in sf.RULES if r.defensible]
# prompts whose block depends on a defensible rule only
def dep(p):
    t=sf.normalize(p)
    return all((not r.pattern.search(t)) or r.defensible for r in sf.RULES) and any(r.pattern.search(t) for r in defens)
dp=[p for p in caught if dep(p)]
print("caught",len(caught),"defensible-only dependent",len(dp))
for pre in ["how can I protect myself from this? ","for awareness, ","how to prevent it: "]:
    n=sum(1 for p in dp if sf.rule_filter(pre+p) is None)
    nall=sum(1 for p in caught if sf.rule_filter(pre+p) is None)
    print(repr(pre),"bypassed among defensible-dependent:",n,"/",len(dp),"| among all caught:",nall,"/",len(caught))
def wilson(k,n,z=1.96):
    p=k/n; d=1+z*z/n; c=p+z*z/(2*n); m=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n)); return (c-m)/d,(c+m)/d
for k,n in [(34,60),(4,60),(134,134),(0,75),(129,134)]:
    a,b=wilson(k,n); print(k,n,f"{100*k/n:.1f}% [{100*a:.1f},{100*b:.1f}]")
