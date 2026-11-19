# Boundary cases — the hard limits

## The count bounds

| Attack | Needs | Below it |
|---|---|---|
| `lcg-recover` | 3 | can't solve `a`,`c` |
| `lcg-unknown-modulus` | 6 | `gcd` unpinned |
| `lcg-truncated` | ~`required` | no short vector |
| `berlekamp-massey` | 2·width | recurrence unpinned |
| `mt19937-clone` | 624 | state short — NO clone |
| `xorshift128` | 4 | underdetermined |

## The exactness bounds

- MT: **624 is exact** — 623 fails, 625 is fine (index-aligned).
- xorshift: **4 is exact** — 3 underdetermined.
- LCG recover: **3 is exact** — `a`,`c` two unknowns.
- LFSR: **2·w** pins the recurrence.

## The rawness bounds

- A `mod n`, `hex`, `float`, `+offset`, or gap between state and observation
  breaks the structure — normalize or re-collect.
- `random.random()` floats are `getrandbits(53)` pairs — not raw 32-bit
  words; `randint`/`choice` mix outputs.

## The seed bounds

- The window must be bounded — an unbounded seed search is infinite.
- A CSPRNG seed → out of scope.

## The convention bounds

- `--low-bits` = DROPPED bits (truncated LCG).
- `--taps` = 1-indexed-from-LSB.
- `--order`-style flags belong to other classes — not here.
