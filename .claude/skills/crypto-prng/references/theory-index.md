# Theory index — the concept → the file → the consequence

## The model

| Concept | File | Consequence |
|---|---|---|
| `state_{i+1}=F`, `G` | `mechanism*` | the attack is `invert(G)`→replay `F` |
| `S/O` floor | `theory*` | the count is information-theoretic |
| linearity | `theory*` | linear `F`/`G` = recoverable |
| one-way `G` | `class-boundary*` | CSPRNG → out |

## The attack math

| Attack | Math | File |
|---|---|---|
| `lcg-recover` | one inverse | `per-attack-lcg-recover*` |
| `lcg-unknown-modulus` | telescope gcd | `per-attack-*` |
| `lcg-truncated` | HNP lattice | `per-attack-*` |
| `berlekamp-massey` | min recurrence | `per-attack-*` |
| `lfsr-*` | GF(2) solve | `per-attack-*` |
| `mt19937-clone` | `untemper` | `per-attack-*` |
| `xorshift128` | linear solve | `per-attack-*` |
| seed | enumerate | `seed-*` |

## The boundaries

| Concept | File |
|---|---|
| combiner `L≈n/2` | `per-family-lfsr-deep` |
| `mod n` vs `>>b` | `edge-*` |
| variants | `real-world-*`,`edge-*` |
