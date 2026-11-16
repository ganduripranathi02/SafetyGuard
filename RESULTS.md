# SafetyGuard results

> **How to read this.** The development sets below were used while writing and adjusting the rules, so their 100% scores measure fit, not generalisation. The held-out result is in the next section.

## Development sets (rules tuned on these)

| Test set | Prompts | Filter blocked | Model refused | Leaked | Errors | Safety score | False positives |
|---|---|---|---|---|---|---|---|
| Original 49 (rules tuned on these) | 49 | 49 | 0 | 0 | 0 | 49/49 = 100.0% | 0/30 |
| Held-out 30 (partly tuned) | 30 | 30 | 0 | 0 | 0 | 30/30 = 100.0% | 0/30 |
| Fresh 25 (partly tuned) | 25 | 25 | 0 | 0 | 0 | 25/25 = 100.0% | 0/25 |
| My own 30 (63% before tuning, then tuned) | 30 | 30 | 0 | 0 | 0 | 30/30 = 100.0% | 0/20 |

## Unseen set (60 harmful, 60 benign, never used for tuning)

| Configuration | Harmful stopped | Benign wrongly stopped |
|---|---|---|
| Rule layer alone | 34/60 = 56.7% | 4/60 = 6.7% |
| Filter (rules + semantic at 0.70) | 35/60 = 58.3% | 4/60 = 6.7% |
| Llama 3.2 alone | 57/60 = 95.0% | 9/60 = 15.0% |
| Full pipeline | 58/60 = 96.7% | 12/60 = 20.0% |

See [`docs/RESULTS_UNSEEN.md`](docs/RESULTS_UNSEEN.md) for the failures, the evasion tests and the ablations.

## Semantic threshold calibration (development sets: 134 harmful, 75 benign)

```
threshold  harmful_caught  benign_blocked
  0.40      107/134         22/75
  0.45       83/134         15/75
  0.50       61/134         10/75
  0.55       45/134          4/75
  0.60       33/134          1/75
  0.65       24/134          1/75
  0.70       18/134          0/75
  0.75       13/134          0/75
  0.80       10/134          0/75
```

## Semantic threshold calibration (unseen set: 60 harmful, 60 benign)

```
threshold  harmful_caught  benign_blocked
  0.40       37/60          21/60
  0.45       29/60          14/60
  0.50       21/60          10/60
  0.55       16/60           8/60
  0.60       13/60           5/60
  0.65       11/60           2/60
  0.70        5/60           0/60
  0.75        3/60           0/60
  0.80        1/60           0/60
```
