# Boundary cases deep — the edges that decide the attack

## The count boundaries — exactly at the floor

### `lcg-recover` — exactly 3

- **At 3**: enough for `a`,`c` IF `gcd(x1-x0,m)=1`. One non-invertible
  difference → need a 4th.
- **At 2**: underdetermined — infinitely many `a`,`c` fit two points.

### `lcg-unknown-modulus` — exactly 6

- **At 6**: two `u` values → a gcd. The gcd may be a MULTIPLE of `m` —
  gather 8+ for a cleaner result.
- **At 5**: one `u` → no gcd → `m` unpinned.

### `lcg-truncated` — the `required` heuristic

- The lattice needs enough `h_i` that the bound `l_i < 2^b` forces a
  unique short vector. Too few → underdetermined.
- `low-bits` near the full width → the leak is tiny → the lattice never
  closes → not solvable this way.

### `berlekamp-massey` — exactly `2w`

- **At 2w**: the minimal recurrence is determined. At `2w-1` → two
  recurrences can fit → wrong taps possible.
- **Extra bits**: refine `L` to convergence — more is strictly better.

### `mt19937-clone` — exactly 624

- **At 624**: the full state — the ONLY count that works.
- **At 623**: one word missing → the twist's index is unknown → no clone.
  Hard boundary.
- **At 625**: 624 recover + 1 verify — the ideal.

### `xorshift128` — exactly 4

- **At 4**: the 128-bit state pinned. At 3 → underdetermined.
- **At 5**: 4 recover + 1 verify — the ideal.

## The convention boundaries — the bit edges

- **`--low-bits` = `b`** — dropped vs kept. `x>>b` → `low-bits=b`. The
  kept count `w-b` is wrong input.
- **`--taps` indexing** — 1-indexed-LSB vs 0-indexed vs MSB-indexed — the
  polynomial mirrors.
- **`--outputs` order** — comma ints in stream order; a sort/reverse/dedup
  breaks "consecutive".

## The rawness boundaries

- **`x mod n` vs `x>>b`** — `mod` is a reduced state (the affine structure
  shifts by `n` each wrap); `>>` is a truncated state (high bits intact).
  `lcg-truncated` is for `>>`/`high-bit` leaks, NOT `mod`.
- **float vs word** — `random()` is a `2^53` pair, not `getrandbits(32)`.
- **hex/base64** — decode, not a different number.

## The seed boundaries

- **`time()` sec vs ms vs ns** — the window's units change the enumeration
  count by 1000×.
- **two-factor seed `pid^time`** — enumerable only if BOTH are bounded.
- **`os.urandom`/`secrets`** — unbounded → out of class.

## The alignment boundary

- a `seed()`/`srand()`/reinit in the window → the collected outputs span
  two streams → the clone/recovery is off.

## The generator boundary — out of class

- CSPRNG/`os.urandom`/`secrets`/keyed cipher output → `crypto-symmetric-oracle`.
- A hash `sha256(x)`/`hmac` → different class.
- A nonce that's NOT a PRNG stream (a counter, a UUID) → different mechanism.
