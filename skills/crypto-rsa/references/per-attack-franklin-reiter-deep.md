# per-attack franklin-reiter deep — the related-message, the full treatment

## The mechanism

`m2 = a·m1 + b` linear, `a`,`b` known, both under `n`,`e`. The polynomials
`x^e - c1` and `(ax+b)^e - c2` in `Z_n[x]` vanish at `x=m` → `gcd` = `x-m` → `m`.

## Detection

- keygen: `m2 = a*m1 + b`, `c1=pow(m1,e,n)`, `c2=pow(m2,e,n)`.
- a linear relation, `e` small.

## The bound / falsifier

A *linear* relation, `a`,`b` known. Non-linear → dead.

## The attack — manual (no `crypto_attack.py` id)

`tools/crypto/franklin_reiter.py` — a standalone module. Or the poly `gcd`:

```python
# gcd of x^e - c1 and (a*x+b)^e - c2 over Z_n[x] = x - m
```

## The chain

`gcd` → `x-m` → `m` → `pow(m,e,n)==c1`.

## The verify

`pow(m,e,n)==c1` — `m` re-encrypts.

## Variants

- `hastad` generalises — `franklin-reiter` is `e`-small, same-`n`, linear.
- A broadcast linear pad — `m_i = a_i·m+b_i` — same mechanism.

## Failure modes

- relation not linear — `a`/`b` unknown or non-linear.
- `e` large — slower but works; the relation is the requirement.

## The honest status

Franklin-Reiter 1995 — catalogue.
