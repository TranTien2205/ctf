# Detection matrix — observation → attack → command

## The full matrix

| Observation | Attack | Command |
|---|---|---|
| LCG, m known, ≥3 outs | `lcg-recover` | `--outputs o --modulus m` |
| LCG, m unknown, ≥6 outs | `lcg-unknown-modulus` | `--outputs o` |
| LCG, high bits only | `lcg-truncated` | `--outputs h --modulus m --a a --c c --low-bits b` |
| LFSR keystream, taps? | `berlekamp-massey` | `--bits b`/`--keystream-hex`/`--bits-file` |
| LFSR, taps unknown | `lfsr-recover` | `--bits b --width w [--taps t]` |
| LFSR, taps known | `lfsr-predict` | `--bits b --taps t --width w --count n` |
| MT, 624 words | `mt19937-clone` | `--outputs o [--count n]` |
| xorshift, 4 words | `xorshift128` | `--outs o --predict n` |
| `seed(time())` | seed-search | bound epoch → `random.seed(ts)` match |

## The count column

| Count | Attack |
|---|---|
| 3 | `lcg-recover` |
| 6+ | `lcg-unknown-modulus` |
| ~`required` | `lcg-truncated` |
| 2·w bits | `berlekamp-massey` |
| 624 | `mt19937-clone` |
| 4 | `xorshift128` |

## The rawness column

| Shape | Route |
|---|---|
| raw ints | direct |
| hex | decode |
| floats | ×2**53 pair or not-cloneable |
| mod n | different problem |
| bits | LFSR family |
