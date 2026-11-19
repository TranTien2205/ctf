# Per-falsifier — every attack → its kill condition → the files

## The per-attack kills

| Attack | Falsifier | Files |
|---|---|---|
| `lcg-recover` | `x1-x0` non-invertible / `predict != held` | `per-attack-lcg-recover.md`,`falsifiers*.md` |
| `lcg-unknown-modulus` | `gcd` no `m` / <6 outs | `per-attack-*.md`,`falsifiers*.md` |
| `lcg-truncated` | `m`,`a`,`c` missing / `predict != held` | `per-attack-*.md`,`falsifiers*.md` |
| `berlekamp-massey` | complexity ≈ stream | `per-attack-*.md`,`falsifiers*.md` |
| `lfsr-recover`/`predict` | predicted diverges | `per-attack-*.md`,`falsifiers*.md` |
| `mt19937-clone` | <624 / `predict != held` | `per-attack-*.md`,`falsifiers*.md` |
| `xorshift128` | <4 / wrong variant | `per-attack-*.md`,`falsifiers*.md` |
| seed-search | unbounded/CSPRNG seed | `per-family-seed.md`,`falsifiers*.md` |

## The class falsifier

`predict != held-back` everywhere → CSPRNG/keyed → wrong class.

## The record

`negative-results*.md` `attempts` `decide.py` rungs.
