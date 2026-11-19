# Theory catalogue — the concepts → the files

## The model concepts

| Concept | Files |
|---|---|
| `state_{i+1}=F(state_i)`, `G` | `theory*`,`mechanism*` |
| the `(F,G)` pairs as code | `mechanism-variant.md` |
| `S/O` information floor | `theory*`,`theory-variant` |
| linearity = vulnerability | `theory*` |
| `G` one-way = boundary | `theory-deep`,`class-boundary*` |

## The per-attack math → files

| Attack | Math | Files |
|---|---|---|
| `lcg-recover` | `(x2-x1)(x1-x0)^{-1}` | `per-attack-lcg-recover*`,`lcg-deep` |
| `lcg-unknown-modulus` | `gcd(t_{i+1}t_{i-1}-t_i^2)` | `per-attack-*`,`lcg-deep` |
| `lcg-truncated` | HNP lattice | `per-attack-*`,`lcg-deep` |
| `berlekamp-massey` | minimal GF(2) recurrence | `per-attack-*`,`lfsr-deep` |
| `lfsr-*` | GF(2) linear solve | `per-attack-*`,`lfsr-deep` |
| `mt19937-clone` | `untemper`×624 | `per-attack-*`,`mt19937-deep` |
| `xorshift128` | 128-bit linear solve | `per-attack-*`,`xorshift-deep` |
| seed | enumerate `init(seed)` | `seed-search-*`,`per-family-seed*` |

## The boundary math → files

| Concept | Files |
|---|---|
| combiner → `L≈n/2` | `per-family-lfsr-deep`,`theory*` |
| `mod n` ≠ `>>b` | `edge-*`,`boundary-*` |
| `128+`/`64*`/`mt_rand`/`java` variants | `real-world-*`,`edge-*` |

## The vocabulary → files

| Term | Files |
|---|---|
| taps/width/low-bits/state/temper | `glossary*` |
| consecutive/raw/truncated/reduced | `glossary*` |
| linear complexity/HNP/untemper | `glossary-deep`,`theory*` |
