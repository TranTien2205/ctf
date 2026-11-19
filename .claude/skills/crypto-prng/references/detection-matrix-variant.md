# Detection matrix variant — observation → the one attack → the flag set

## The compact matrix

| Observation | Attack | Command |
|---|---|---|
| `m` known, 3+ raw outs | `lcg-recover` | `--outputs o --modulus m` |
| `m` unknown, 6+ raw outs | `lcg-unknown-modulus` | `--outputs o` |
| `x>>b` leak, `a`,`c`,`m` | `lcg-truncated` | `--outputs h --modulus m --a a --c c --low-bits b` |
| bitstream, taps? | `berlekamp-massey` | `--bits b`/`--keystream-hex`/`--bits-file` |
| bitstream, taps+width | `lfsr-predict` | `--bits b --taps t --width w --count n` |
| bitstream, width | `lfsr-recover` | `--bits b --width w` |
| 624 raw words | `mt19937-clone` | `--outputs o`/`--outputs-file f` |
| 4 raw words | `xorshift128` | `--outs o --predict n` |
| `seed=f(small)`+window | seed-search | `random.seed(ts)` loop |

## The count column — the gate

| Count | Attack |
|---|---|
| 3 | `lcg-recover` |
| 6+ | `lcg-unknown-modulus` |
| ~required | `lcg-truncated` |
| 2·w | `berlekamp-massey` |
| ≥w | `lfsr-predict`/`lfsr-recover` |
| 624 | `mt19937-clone` |
| 4 | `xorshift128` |
| bounded | seed-search |

## The shape column — the normalizer

| Shape | Route |
|---|---|
| raw ints | direct |
| `x>>b` | `lcg-truncated` |
| `x mod n` | different model |
| float | `×2^53`/variant |
| hex/b64 | decode |
| bits | LFSR |
| `Math.random` | `xorshift128+` — different |

## The falsifier column

`predict != held` → troubleshoot → falsifier → attempts → decide.py.
