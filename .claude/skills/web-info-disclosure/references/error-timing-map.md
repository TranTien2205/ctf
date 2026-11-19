# Error timing — the hidden distinguisher — map


## Signals

| Observation | Meaning | Route |
|---|---|---|
| identical 500s, one slower | timing distinguishes | measure 50+ samples |
| bcrypt/hash error vs parse error | different cost | timing oracle |
| cache-hit vs miss responses | cache layer revealed | timing + X-Cache |

## Falsifier

Falsifier — indistinguishable distributions at 200+ samples: no timing signal.
