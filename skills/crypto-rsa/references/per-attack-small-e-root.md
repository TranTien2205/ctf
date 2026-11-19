# small-e-root / nth-root — the wrap attack, complete

## What it is

`c = m^e` with `m^e < n` → the modulo never wrapped → `m` is the plain `e`th
root of `c`, not a modular root.

## The mechanism

`c = m^e mod n`; if `m^e < n` then `c = m^e` exactly — an integer power.
`m = c^{1/e}` via `integer_nthroot`.

## Detection

- **`e` small** — 3, 5, 17, 257.
- **`m` short** — a short flag or a small `m` relative to `n` (`m^e<n`).
- **no pad** — the keygen encrypts `m` raw.

## The bound / falsifier

`m^e < n`. `m^e ≥ n` → wrapped → dead; route `hastad`/`coppersmith`.

## The attack

```python
from sympy import integer_nthroot
m, exact = integer_nthroot(c, e)
assert exact and pow(m, e) == c   # no mod n
```

Or: `crypto_attack.py small-e-root --c <c> --e 3 --n <n>`.

## The verify

`pow(m,e)==c` — plain, no `mod n` — the wrap never happened.

## Variants

- `nth-root` — the general `e`th root (same attack, general `e`).
- A wrapped `m` → `hastad` (e moduli) or `coppersmith` (partial `m`).

## Failure modes

- `m^e ≥ n` — `c` is a true modular residue → not a power.
- A pad applied → `m` differs → not a root.

## The honest status

Standard published attack — catalogue.
