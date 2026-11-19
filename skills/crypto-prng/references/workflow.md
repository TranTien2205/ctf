# Workflow — the solve loop

## The loop

```
collect outputs (consecutive, raw)
  → fingerprint the generator
  → count vs the floor
  → normalize to raw ints
  → pick the attack (the params-known column)
  → run crypto_attack.py <id> / xorshift128.py
  → predict == held-back?
      yes → use → flag → post-probe/pre-flag → record
      no  → troubleshoot → falsifier → attempts → decide.py
```

## The gates in order

1. **generator** — which family (lcg/lfsr/mt/xorshift/seed).
2. **count** — 3/6/required/2w/624/4.
3. **raw+consecutive** — ints, no gaps, no reseed.
4. **params** — `m`/`a`,`c`/taps/width/`low-bits`/window.
5. **verify** — `predict==held-back`.

## The attack table

| Family | Condition | Attack |
|---|---|---|
| LCG | `m` known | `lcg-recover` |
| LCG | `m` unknown | `lcg-unknown-modulus` |
| LCG | `a,c,m`+`x>>b` | `lcg-truncated` |
| LFSR | taps known | `lfsr-predict` |
| LFSR | taps unknown | `berlekamp-massey`→`lfsr-recover` |
| MT | 624 words | `mt19937-clone` |
| xorshift | 4 words | `xorshift128` |
| seed | bounded window | enumerate |

## The close

- `predict==held` → use → `flag{` → `post-probe`/`pre-flag`.
- `predict!=held` → falsifier → `attempts` → `decide.py`.

## The files

`per-attack-*` the attack · `per-family-*` the family ·
`payload-dictionary*` the command · `verify*` the gate ·
`troubleshoot*`/`negative-results*` the failure path.
