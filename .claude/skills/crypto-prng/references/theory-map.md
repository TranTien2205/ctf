# Theory map — the concept → the file

## The model

| Concept | File |
|---|---|
| `state_{i+1}=F(state_i)`, `G(state)` | `theory*.md`,`mechanism*.md` |
| the `(F,G)` pairs as code | `mechanism-variant.md` |
| the `S/O` count floor | `theory*.md`,`per-boundary*.md` |
| linearity = vulnerability | `theory*.md`,`theory-variant.md` |

## The per-attack math

| Attack | Math | File |
|---|---|---|
| `lcg-recover` | one modular inverse | `lcg-recover-deep.md`,`per-attack-*.md` |
| `lcg-unknown-modulus` | telescope + gcd | `lcg-unknown-modulus-deep.md` |
| `lcg-truncated` | HNP lattice | `lcg-truncated-deep.md` |
| `berlekamp-massey` | minimal recurrence | `berlekamp-massey-deep.md` |
| `lfsr-*` | GF(2) linear solve | `lfsr-*.md`,`lfsr-deep.md` |
| `mt19937-clone` | untemper ×624 | `mt19937-*.md` |
| `xorshift128` | 128-bit linear solve | `xorshift-*.md` |
| seed-search | enumerate `state_0` | `seed-search-deep.md` |

## The boundary math

| Concept | File |
|---|---|
| why CSPRNG resists | `theory-deep.md`,`class-boundary*.md` |
| why combiner falsifies BM | `per-family-lfsr-deep.md`,`theory*.md` |
| why `mod n` ≠ `>>b` | `edge-cases*.md`,`boundary-cases*.md` |

## The vocabulary

| Term | File |
|---|---|
| taps/width/low-bits/state | `glossary*.md` |
| consecutive/raw/truncated | `glossary*.md`,`edge-cases*.md` |
| linear complexity/HNP | `glossary-deep.md`,`theory*.md` |
