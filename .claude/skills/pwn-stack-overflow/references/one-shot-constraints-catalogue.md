# One-shot constraints — no re-trigger — case catalogue

The service runs once: no leak-then-exploit. The whole attack must fit a single input — or the leak must be embedded.

## Cases

| # | Shape | Meaning | Route |
|---|---|---|---|
| 1 | service exits after one input | one-shot | single payload |
| 2 | no way to re-prompt | can't re-trigger | combine stages |

## Falsifier

Falsifier — the chain genuinely needs two stages and the service is one-shot: find a leak-free alternative or a different bug.
