# The catch-all falsifier — the discipline — signal map


## Signals

| Observation | Meaning | Route |
|---|---|---|
| Same byte-length body on /env and /notreal | catch-all | all 'hits' are null |
| 404 template differs from probe 200s | real discriminator | compare content |
| Random path gives real 404 while probe paths 200 | no catch-all | status is meaningful |

## Falsifier

Falsifier — every probed path byte-matches the absent-path baseline: nothing was disclosed; the whole sweep is negative.
