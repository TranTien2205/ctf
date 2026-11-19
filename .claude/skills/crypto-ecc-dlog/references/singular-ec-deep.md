# Singular curves — `singular_ec.py`

## When it applies

A custom `y² = x³ + ax + b` where the discriminant vanishes:

```
Δ = -16(4a³ + 27b²) ≡ 0  mod p
```

The curve is singular — it has a node or a cusp at the singular point, and
the nonsingular points form a group isomorphic to either the additive group
`Fp+` (cusp) or a multiplicative group `Fp*` (node). The ECDLP becomes a
*linear or standard finite-field dlog* — vastly easier.

## Detection

Compute `4a³ + 27b² mod p` — if it's `0`, the curve is singular.

## The tool

```bash
python3 tools/crypto/singular_ec.py --selftest
```

The module maps `P, Q` through the isomorphism, solves the resulting dlog in
`Fp+` (one modular inverse — trivial) or `Fp*` (standard dlog — use
`pohlig-hellman`/`bsgs` on the image), and returns `x`.

## The math (sketch)

- **Cusp** — parameterize by the tangent at the singular point; group law
  becomes addition `x ↦ slope(P)`. `x·P = Q` → `x = slope(Q)/slope(P) mod p`.
- **Node** — group law becomes multiplication in `Fp*` (or `Fp²*` for a
  non-split node); then `dlog` with `pohlig-hellman` if `p-1` smooth, else
  `bsgs`/`index-calculus` bounds apply.

## Preconditions

- The supplied `P, Q` are *nonsingular* points — the singular point itself
  isn't in the group.
- For node case: `p-1` should be smooth for PH, else bounded `x` for BSGS.

## Falsifier

`x·P ≠ Q` → wrong singularity type (cusp vs node misidentified), points on
the wrong curve, or `Δ ≠ 0` (not actually singular — check arithmetic).

## Common mistakes

- Solving ECDLP directly on a singular curve — pointless; map first.
- Confusing a singular cubic with anomalous — different checks, different
  tools (`Δ == 0` vs `#E == p`).
