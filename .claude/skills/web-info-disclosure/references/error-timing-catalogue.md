# Error timing — the hidden distinguisher — case catalogue

When two error types produce identical text, timing still separates them: a crypto-check error is slower than a parse error.

## Cases

| # | Shape | Meaning | Route |
|---|---|---|---|
| 1 | identical 500s, one slower | timing distinguishes | measure 50+ samples |
| 2 | bcrypt/hash error vs parse error | different cost | timing oracle |
| 3 | cache-hit vs miss responses | cache layer revealed | timing + X-Cache |

## Falsifier

Falsifier — indistinguishable distributions at 200+ samples: no timing signal.
