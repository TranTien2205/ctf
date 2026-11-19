# Troubleshoot variant — `predict != held`, the compact ladder

## The universal ladder

```
predict != held
  → convention?  (low-bits / taps / modulus / order)
  → variant?     (mt_rand / 128+ / java / glibc)
  → norm?        (float / mod / randint / hex)
  → align?       (gap / reseed)
  → count?       (<floor)
  → still fail → falsifier → attempts → decide.py
```

## `lcg-*` fails

- `gcd(x1-x0,m)!=1` → odd diff / factor `m`.
- `predict!=held` → wrong `m` / non-raw / non-consecutive.
- `gcd→0/1` → not affine → re-fingerprint.
- `low-bits` wrong → recount DROPPED bits.

## `lfsr-*` fails

- `L≈n/2` → combiner → correlation.
- `predict` diverges → taps convention / bit order / width.

## `mt19937-clone` fails

- `<624` → collect / seed-search.
- `predict!=held` → non-raw / gap / reseed / `mt_rand`.

## `xorshift128` fails

- `predict!=held` → `128+`/64* variant / non-consecutive.

## seed-search fails

- no match → widen window / reproduce the call / wrong generator.
