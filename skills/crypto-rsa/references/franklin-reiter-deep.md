# franklin-reiter deep — the related-message attack, the full treatment

## The mechanism

`m2 = a·m1 + b` linear, `a`,`b` known, both encrypted under the same `n`,`e`.
The polynomials `x^e - c1` and `(ax+b)^e - c2` in `Z_n[x]` both vanish at `x=m`
→ their `gcd` is the linear `x - m` → `m` directly.

## Detection

- **keygen**: `m2 = a*m1 + b`, `c1=pow(m1,e,n)`, `c2=pow(m2,e,n)` — a linear
  relation between the messages.
- **the tell**: two related messages, `e` small.

## The bound / falsifier

A *linear* relation with `a`,`b` known. Non-linear → dead; a different
relation → a different attack.

## The attack — manual (no `crypto_attack.py` id)

```python
# the gcd of x^e - c1 and (a*x+b)^e - c2 over Z_n[x] = x - m
# in sympy / a polynomial gcd over GF(n) — m is the root
```

`tools/crypto/franklin_reiter.py` exists as a standalone module — it is not a
`crypto_attack.py` id. Run it or the manual `gcd` directly.

## The chain

`gcd` of the polynomials → `x - m` → `m` → `pow(m,e,n)==c1` verify.

## The verify

`pow(m,e,n)==c1` — the recovered `m` re-encrypts.

## Worked shape

```
m2 = 2·m1 + 7,  e=3,  same n
f1(x) = x³ - c1,  f2(x) = (2x+7)³ - c2
gcd(f1,f2) over Z_n[x] = x - m   →   m
```

## Variants

- `hastad` generalises this — `franklin-reiter` is the `e`-small, same-`n`,
  linear case.
- A **broadcast with a linear pad** — `m_i = a_i·m + b_i` — the same mechanism.
- `m2` a non-linear function of `m1` → the `gcd` isn't linear → dead.

## Failure modes

- relation not linear — `a`/`b` unknown or non-linear.
- `e` large — the `gcd` is slower but works; the relation is the requirement.

## The honest status

Franklin-Reiter 1995 — catalogue.
