# Mechanism index — the primitives → the files

## The ECDSA primitives

| Primitive | Files |
|---|---|
| `s = k⁻¹(z + d·r) mod n` | `theory*.md`,`mechanism*.md` |
| reuse `k` → `d` closed form | `ecdsa-nonce-reuse-deep.md`,`mechanism-deep.md` |
| bias `k < B` → HNP lattice | `hnp-ecdsa-deep.md`,`hnp-deep.md`,`mechanism-deep.md` |
| `t = s⁻¹r`, `u = -s⁻¹z` | `hnp-deep.md`,`theory-deep.md` |

## The DLP primitives

| Primitive | Files |
|---|---|
| `h = g^x mod p` | `per-family-dlog.md`,`theory*.md` |
| PH per-factor + CRT | `pohlig-hellman-deep.md`,`mechanism-deep.md` |
| BSGS `√n` | `bsgs-deep.md`,`mechanism-deep.md` |
| `smoothness` factorization | `smoothness-deep.md` |

## The defect primitives

| Primitive | Files |
|---|---|
| `#E == p` p-adic lift | `smart-attack-deep.md`,`mechanism-deep.md` |
| `Δ == 0` `Fp+`/`Fp*` iso | `singular-ec-deep.md`,`mechanism-deep.md` |
| unvalidated `d·P'` | `invalid-curve-deep.md`,`mechanism-deep.md` |

## The verify primitives

| Primitive | Files |
|---|---|
| `x·G == Q` | `verify*.md`,`per-check*.md` |
| `pow(g, x, p) == h` | `verify*.md`,`per-check*.md` |
| `pow(h, ord, p) == 1` | `per-check*.md` |
