# Error timing — the hidden distinguisher

When two error types produce identical text, timing still separates them: a crypto-check error is slower than a parse error.

## Signals

| Observation | Meaning | Route |
|---|---|---|
| identical 500s, one slower | timing distinguishes | measure 50+ samples |
| bcrypt/hash error vs parse error | different cost | timing oracle |
| cache-hit vs miss responses | cache layer revealed | timing + X-Cache |

## Steps

1. Baseline the two error types with 50+ samples each.
2. Compare medians — a separated distribution is a signal.
3. Cache timing reveals whether a resource was fetched before (xs-leaks adjacent).
4. If distributions overlap at 200 samples, the channel is dead.

## Falsifier

Falsifier — indistinguishable distributions at 200+ samples: no timing signal.

## Traps

- Timing is the last resort — always prefer content/status distinguishers.
- Warmup and jitter correction are mandatory.
- This boundary overlaps web-xs-leaks.

## Commands

```bash
for i in $(seq 50); do curl -s -o /dev/null -w '%{time_total}\n' '$BASE/bad1'; done
```

## Cross-references

`response-anatomy.md` · `evidence.md`
