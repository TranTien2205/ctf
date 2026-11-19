# Verify catalogue — every check indexed

## The per-attack verify

| Attack | Verify | File |
|---|---|---|
| `ecdsa-nonce-reuse` | `d·G == Q` | `verify*.md` |
| `hnp-ecdsa`/`hnp` | `d·G == Q` (`--curve`/`--pubkey` inside) | `verify*.md`,`hnp-ecdsa-deep.md` |
| `pohlig-hellman` | `pow(g, x, p) == h` | `verify*.md` |
| `bsgs` | `pow(g, x, p) == h` | `verify*.md` |
| `smart_attack` | `x·P == Q` | `verify*.md` |
| `singular_ec` | `x·P == Q` | `verify*.md` |
| invalid curve | `d·G == Q` (real curve) | `verify*.md`,`invalid-curve-deep.md` |

## The prechecks

| Check | File |
|---|---|
| `pow(h, ord, p) == 1` (`h ∈ <g>`) | `per-check*.md` |
| `n·G == ∞` | `verify*.md` |
| point on curve `y² == x³+ax+b` | `invalid-curve-deep.md` |

## The flag verify

| Check | File |
|---|---|
| `flag{`/`CTF{` present | `verify*.md`,`evidence*.md` |

## The record verify

| Check | File |
|---|---|
| `post-probe` evidence ⊆ response | `evidence*.md` |
