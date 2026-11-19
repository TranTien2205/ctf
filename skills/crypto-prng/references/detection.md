# Detection — name the generator before attacking

## The order

1. **name** — grep the generator name in source; free.
2. **shape** — bits/words/floats/mod-ints; free.
3. **count** — `len(outputs)` vs the floor; free.
4. **fingerprint** — gcd/BM/clone-test; cheap.
5. **seed** — `seed=`/`srand`/`iat` bound; cheap.

## The signals

- `mt19937`/`xorshift`/`lfsr`/`lcg`/`rand`/`srand`/`seed` → the family.
- `os.urandom`/`secrets`/`crypto.`/`SecureRandom`/`arc4random` → **out**.
- `mt_rand`/`java.util.Random`/`Math.random`/`drand48`/`rand` → the
  platform variant — same family, different constants.

## The shape → family

| Shape | Family |
|---|---|
| bits | LFSR |
| mod-`m` ints | LCG |
| raw 32-bit words | MT/xorshift |
| floats | `random()`/`Math.random` |
| time-coupled | seed-search |

## The fingerprint tests

- **LCG**: `gcd(t_{i+1}·t_{i-1}-t_i^2)` → stable `m`.
- **LFSR**: Berlekamp-Massey → `L` « n.
- **MT**: `mt19937-clone` → `predict==held`.
- **xorshift**: `xorshift128` → `predict==held`.

## The count floors

3 (`lcg-recover`) · 6 (`lcg-unknown-modulus`) · required (`lcg-truncated`)
· 2w (`berlekamp`) · 624 (`mt19937-clone`) · 4 (`xorshift128`).

## The route

`detection-matrix.md` for the full matrix; `per-attack-*` for the attack;
`payload-dictionary*` for the command.
