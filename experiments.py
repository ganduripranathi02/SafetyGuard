import os, re, time, json, statistics
os.environ["SG_SEMANTIC"]="0"
import safety_filter as sf

L=lambda p:[l.strip() for l in open(p,encoding='utf-8') if l.strip()]
tuned_h = L('adversarial_prompts.txt')+L('held_out_harmful.txt')+L('fresh_harmful.txt')+L('my_test_harmful.txt')
tuned_b = L('benign_prompts.txt')+L('fresh_benign.txt')+L('my_test_benign.txt')
un_h, un_b = L('unseen_harmful.txt'), L('unseen_benign.txt')
print(len(tuned_h),len(tuned_b),len(un_h),len(un_b))

def rate(fn, prompts): return sum(1 for p in prompts if fn(p))
blk = lambda p: sf.rule_filter(p) is not None

# ---- 1. headline
res={}
res['tuned_recall']=(rate(blk,tuned_h),len(tuned_h)); res['tuned_fp']=(rate(blk,tuned_b),len(tuned_b))
res['unseen_recall']=(rate(blk,un_h),len(un_h)); res['unseen_fp']=(rate(blk,un_b),len(un_b))

# unseen recall split: injection-style vs content
inj_kw=re.compile(r"instruction|policy|ethic|safety training|filters|roleplay|pretend|act as|from this point|no longer|hidden", re.I)
# ---- 2. obfuscation
def upper(p): return p.upper()
def leet(p): return p.translate(str.maketrans("aeiosAEIOS","4310 54310 5".replace(" ","")[:10])) if False else re.sub(r"[aeios]",lambda m:{"a":"4","e":"3","i":"1","o":"0","s":"5"}[m.group(0)],p.lower())
def zwsp(p): return "".join(c+("\u200b" if i%2 else "") for i,c in enumerate(p))
def dotted(p): return " ".join(".".join(w) if len(w)>=3 and w.isalpha() else w for w in p.split())
def spaced(p): return " ".join(" ".join(w) if len(w)>=4 and w.isalpha() else w for w in p.split())
CY=str.maketrans("aeopcxy","аеорсху")
def homog(p): return p.translate(CY)
def accents(p): 
    import unicodedata
    return "".join(c+("\u0301" if c in "aeiou" else "") for c in p)
T={'original':lambda p:p,'uppercase':upper,'leetspeak':leet,'zero-width':zwsp,'dotted':dotted,'accents':accents,'spaced letters':spaced,'homoglyph':homog}
base=[p for p in tuned_h if blk(p)]   # only prompts caught in clear form
print("clear-caught base:",len(base))
obf={}
for name,f in T.items():
    obf[name]=rate(blk,[f(p) for p in base])
# no-normalisation ablation
orig_norm=sf.normalize
sf.normalize=lambda t:t.lower()
obf_nonorm={name:rate(blk,[f(p) for p in base]) for name,f in T.items()}
sf.normalize=orig_norm

# ---- 3. defensive override ablation
orig_def=sf._DEFENSIVE
sf._DEFENSIVE=re.compile(r"(?!x)x")
abl={'with_override':{'tuned_fp':rate(blk,tuned_b),'unseen_fp':rate(blk,un_b),'tuned_recall':rate(blk,tuned_h),'unseen_recall':rate(blk,un_h)}}
abl['without_override']={'tuned_fp':rate(blk,tuned_b),'unseen_fp':rate(blk,un_b),'tuned_recall':rate(blk,tuned_h),'unseen_recall':rate(blk,un_h)}
sf._DEFENSIVE=orig_def
abl['with_override']={'tuned_fp':rate(blk,tuned_b),'unseen_fp':rate(blk,un_b),'tuned_recall':rate(blk,tuned_h),'unseen_recall':rate(blk,un_h)}

# ---- 4. category stats
from collections import Counter
cats=Counter(r.category for r in sf.RULES)
dcount=sum(r.defensible for r in sf.RULES)
catblk=Counter(sf.rule_filter(p) for p in tuned_h+un_h)

# ---- 5. latency
allp=tuned_h+tuned_b+un_h+un_b
t=[]
for p in allp:
    s=time.perf_counter(); sf.screen(p); t.append((time.perf_counter()-s)*1000)
lat=dict(mean=statistics.mean(t),median=statistics.median(t),p95=sorted(t)[int(.95*len(t))],max=max(t))

out=dict(res=res,obf=obf,obf_nonorm=obf_nonorm,base=len(base),abl=abl,rules=len(sf.RULES),defensible=dcount,cats=dict(cats),lat=lat)
print(json.dumps(out,indent=1))
import os; os.makedirs('results',exist_ok=True); json.dump(out,open('results/exp.json','w'),indent=1)
