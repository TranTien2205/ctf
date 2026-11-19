# Payload map — flag → meaning → gotcha

## The input flags

| Flag | Means | Gotcha |
|---|---|---|
| `--outputs` | comma ints, stream order | no sort/dedup; raw ints only |
| `--outputs-file` | file of outputs | one per line / JSON list |
| `--outs` | xorshift outputs | standalone `tools/crypto/` module |
| `--bits` | comma `0/1` | not a hex bitstring |
| `--keystream-hex` | hex stream | per-byte bit order matters |
| `--bits-file` | file of bits | one form |
| `--in FILE` | JSON all-params | alternative to individual flags |

## The param flags

| Flag | Means | Gotcha |
|---|---|---|
| `--modulus` | LCG `m` | `lcg-recover`/`lcg-truncated` only — `lcg-unknown-modulus` takes none |
| `--a` | LCG `a` | required for `lcg-truncated` |
| `--c` | LCG `c` | required for `lcg-truncated` |
| `--low-bits` | DROPPED bits `b` | NOT the kept bits — the #1 trap |
| `--taps` | LFSR taps | 1-indexed-from-LSB |
| `--width` | LFSR `w` | required for `lfsr-*` |
| `--count` | next n outputs | `lfsr-predict`/`mt19937-clone`/`xorshift` |

## The meta flags

| Flag | Means |
|---|---|
| `--json` | compact machine output |
| `--selftest` | offline proof (xorshift128 only) |
| `--help` | real flags per id |

## The gotchas ranked by frequency

1. `--low-bits` = DROPPED, passed as KEPT — wrong bound.
2. `--taps` indexing — wrong convention → `predict` diverges.
3. `--outputs` non-raw (float/mod/hex) — wrong states.
4. `--outputs` on `lcg-unknown-modulus` with a `--modulus` — it takes none.
5. `xorshift128` as `crypto_attack.py` id — it's `tools/crypto/xorshift128.py`.
6. `mt19937-clone` on non-`getrandbits(32)` words — `random()`/`randint`.

## The library forms (no CLI)

```python
from tools.crypto import lcg, lfsr, mt19937, xorshift128, numtheory
# these have no __main__ — import only
```
