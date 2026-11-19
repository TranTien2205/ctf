# `smoothness` — the order factorization gate

## When it runs

**First, always**, for any `h = g^x mod p` or `Q = x·P` where the order is
in doubt. It's seconds and it decides the whole route.

## The command

```bash
python3 tools/crypto_attack.py smoothness --n 1092924092708206891
```

`numtheory.smoothness` factors `n` and reports the factors plus the largest
prime factor.

## Reading the result

| Largest prime factor | Route |
|---|---|
| ≤ ~2²⁰ | `pohlig-hellman` — trivial |
| 2²⁰ .. 2⁴⁰ | `pohlig-hellman` — feasible, slower |
| > 2⁴⁰ | PH dies in the largest factor — look elsewhere |
| `n` is prime | generic methods only — `bsgs` ceiling applies |
| `n = 2q`, `q` large prime | safe prime — designed-resistant |

## Which `n` to factor

- Finite-field DLP: `p-1` for a generator `g`, else `ord(g)`.
- Curve DLP: `#E(Fp)` — the point count, which the challenge supplies or you
  compute (Schoof — out of scope; the handout almost always gives it).
- ECDSA: not `n` — the nonce attacks don't need smoothness.

## On curves

A smooth `#E` → run PH with point arithmetic (the same math, `ec.py` for the
ops). A prime `#E` near `p` → generic-hard, look for defects instead.

## The falsifier

`smoothness` failing to factor fully → Pollard-rho/`numtheory` limits —
the order is probably fine to be prime-ish anyway. The *real* falsifier is
PH's largest-factor check.

## Common mistakes

- Factoring `p` instead of `p-1`.
- Factoring the field size for a curve when you need `#E`.
- Skipping the check and going straight to `bsgs` on a large group.
