# Per-boundary — every bound → the value → the files

## The count bounds

| Bound | Value | Files |
|---|---|---|
| `lcg-recover` | 3 outs | `boundary-cases*.md`,`per-attack-lcg-recover.md` |
| `lcg-unknown-modulus` | 6 outs | `boundary-cases*.md`,`per-attack-*.md` |
| `lcg-truncated` | `required` heuristic | `boundary-cases*.md`,`per-attack-*.md` |
| `berlekamp-massey` | 2·width bits | `boundary-cases*.md` |
| `mt19937-clone` | 624 words | `boundary-cases*.md`,`per-attack-*.md` |
| `xorshift128` | 4 outs | `boundary-cases*.md`,`per-attack-*.md` |

## The convention bounds

| Bound | Value | Files |
|---|---|---|
| `--low-bits` | DROPPED bits | `common-mistakes*.md`,`per-attack-lcg-truncated.md` |
| `--taps` | 1-indexed-from-LSB | `per-attack-*.md` |
| `--outputs` | comma ints / `-file` | `payload-dictionary*.md` |
| MT word | raw `getrandbits(32)` | `per-attack-mt19937-clone.md` |

## The seed bounds

| Bound | Value | Files |
|---|---|---|
| window | bounded epoch | `per-family-seed.md` |
| CSPRNG | out of scope | `class-boundary*.md` |

## The falsifier bound

`predict != held-back` — the universal kill.
