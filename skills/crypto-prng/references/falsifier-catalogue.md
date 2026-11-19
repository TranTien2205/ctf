# Falsifier catalogue — every falsifier → the mechanism it kills → the action

## The falsifier → kill → action table

| Falsifier | Kills | Action |
|---|---|---|
| `gcd→0/1` | affine structure | re-fingerprint — not LCG |
| `L≈n/2` | plain LFSR | combiner → correlation |
| `predict!=held` (lcg-recover) | wrong `m`/non-raw | re-derive `m`/normalize |
| `predict!=held` (unknown-mod) | wrong `m` | factor the gcd |
| `predict!=held` (truncated) | `low-bits`/params | recount `b`/re-derive |
| `predict!=held` (lfsr) | taps/width/order | re-index/flip |
| `predict!=held` (mt) | <624/non-raw/gap/reseed | collect/seed-search |
| `predict!=held` (xorshift) | variant (`128+`/64*) | the `+` tool |
| `predict!=held` (seed) | window/call | widen/fix call |
| `predict!=held` everywhere | wrong class | reclassify |

## The kills ranked by severity

```
class kill (predict!=held everywhere / CSPRNG named) → reclassify
mechanism kill (the model falsified) → troubleshoot → falsifier → attempts
param kill (a convention/param wrong) → fix + retry
count kill (under floor) → collect more
```

## The action ladder

```
falsifier → troubleshoot* → still fail → attempts + reopen_if
→ decide.py rung → stop when rungs spent
```

## The record

`negative-map`/`negative-results*` — the falsifier + `reopen_if`.
