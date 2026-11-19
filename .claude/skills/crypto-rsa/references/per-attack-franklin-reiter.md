# franklin-reiter — the related-message attack, complete

## What it is

`m2 = a·m1 + b` linear, `a`,`b` known, both encrypted under the same `n`,`e` —
`gcd(x^e - c1, (ax+b)^e - c2)` in `Z_n[x]` = `x - m`.

## The mechanism

`x^e - c1` and `(ax+b)^e - c2` both vanish at `x=m` mod `n` → their `gcd` is the
linear `x - m` → `m` directly.

## Detection

- **keygen**: `m2 = a*m1 + b`, `c1=pow(m1,e,n)`, `c2=pow(m2,e,n)` — a linear
  relation.
- **the tell**: two related messages, `e` small.

## The bound / falsifier

A *linear* relation with `a`,`b` known. Non-linear → dead; a different
relation → a different attack.

## The attack

`franklin-reiter --n <n> --e <e> --a <a> --b <b> --c1 <c1> --c2 <c2>`.

## The chain

`gcd` of the polynomials → `x - m` → `m` → `pow(m,e,n)==c1` verify.

## The verify

`pow(m,e,n)==c1` — the recovered `m` re-encrypts.

## Variants

- `hastad` generalises this — `franklin-reiter` is the `e`-small, same-`n`,
  linear case.
- A **broadcast with a linear pad** — `m_i = a_i·m + b_i` — the same mechanism.

## Failure modes

- relation not linear — `a`/`b` unknown or non-linear.
- `e` large — the `gcd` is slower but works; the relation is the requirement.

## The honest status

Standard published attack (Franklin-Reiter 1995) — catalogue.
