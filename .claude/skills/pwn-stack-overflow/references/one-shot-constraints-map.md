# One-shot constraints — no re-trigger — map


## Signals

| Observation | Meaning | Route |
|---|---|---|
| service exits after one input | one-shot | single payload |
| no way to re-prompt | can't re-trigger | combine stages |

## Falsifier

Falsifier — the chain genuinely needs two stages and the service is one-shot: find a leak-free alternative or a different bug.
