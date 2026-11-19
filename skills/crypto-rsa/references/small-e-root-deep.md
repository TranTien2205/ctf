# small-e-root / nth-root deep — the wrap attack, the full treatment

## The mechanism

`c = m^e` with `m^e < n` → the modulo never engaged → `c` is a plain integer
power. `m = c^{1/e}` via `integer_nthroot`.

## Detection

- **`e` small** — 3, 5, 17, 257.
- **`m` short** — a short flag or a small `m` relative to `n` (`m^e<n`).
- **no pad** — the keygen encrypts `m` raw.
- **`c` small** — `c` may even fit a machine word if `m^e` is tiny.

## The bound / falsifier

`m^e < n`. `m^e ≥ n` → wrapped → dead; route `hastad`/`coppersmith`. Check
`m.bit_length()*e` vs `n.bit_length()` on the sheet.

## The attack

```python
from sympy import integer_nthroot
m, exact = integer_nthroot(c, e)
assert exact and pow(m, e) == c   # no mod n — the wrap never happened
```

Or: `crypto_attack.py small-e-root --n <n> --e <e> --c <c>` /
`nth-root --x <x> --n <n>`.

## The verify

`pow(m,e)==c` — plain, no `mod n` — the wrap never happened.

## Worked shape

```
e=3, m = a 40-byte flag, n = 2048-bit
m³ ≈ 2^960 < n ≈ 2^2048  →  c = m³ exactly  →  m = c^{1/3}
```

## Variants

- `nth-root` — the general `e`th root (the same mechanism, general `e`).
- A wrapped `m` → `hastad` (e moduli) or `coppersmith` (partial `m`).

## Failure modes

- `m^e ≥ n` — `c` is a true modular residue → not a power.
- A pad applied → `m` differs → not a root.

## The honest status

Standard published attack — catalogue.
