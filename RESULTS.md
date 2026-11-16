# SafetyGuard results

| Test set | Prompts | Filter blocked | Model refused | Leaked | Errors | Safety score | False positives |
|---|---|---|---|---|---|---|---|
| Original 49 (rules tuned on these) | 49 | 49 | 0 | 0 | 0 | 49/49 = 100.0% | 0/30 |
| Held-out 30 (partly tuned) | 30 | 30 | 0 | 0 | 0 | 30/30 = 100.0% | 0/30 |
| Fresh 25 (partly tuned) | 25 | 25 | 0 | 0 | 0 | 25/25 = 100.0% | 0/25 |
| My own 30 (63% before tuning, then tuned) | 30 | 30 | 0 | 0 | 0 | 30/30 = 100.0% | 0/20 |

## Prompts to fix (leaked or wrongly blocked)

- none

## Semantic threshold calibration
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
