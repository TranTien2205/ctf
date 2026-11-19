# Attack catalogue — every attack id, one row each

| Attack id | Family | Inputs | Count | Output | Falsifier |
|---|---|---|---|---|---|
| `lcg-recover` | LCG | `--outputs`,`--modulus` | 3 | `a`,`c`,`next` | `predict!=held`/noninvertible |
| `lcg-unknown-modulus` | LCG | `--outputs` | 6 | `m`,`a`,`c` | gcd→0/1 |
| `lcg-truncated` | LCG | `--outputs`,`--modulus`,`--a`,`--c`,`--low-bits` | ~required | state | `predict!=held` |
| `berlekamp-massey` | LFSR | `--bits`/`--keystream-hex`/`--bits-file` | 2w | `(w,taps)` | `L≈n/2` |
| `lfsr-recover` | LFSR | `--bits`,`--width`[,`--taps`] | ≥2w | `(reg,taps)` | predict diverges |
| `lfsr-predict` | LFSR | `--bits`,`--taps`,`--width`,`--count` | ≥w | next bits | predict diverges |
| `mt19937-clone` | MT | `--outputs`/`--outputs-file`[,`--count`] | 624 | clone,next | `predict!=held` |
| `xorshift128` | xorshift | `--outs`,`--predict` | 4 | state,next | `predict!=held` |
| seed-search | seed | `random.seed(ts)` loop | window | seed,next | no match in window |

## The command shapes

```bash
crypto_attack.py <id> --<flags>            # the dispatched form
crypto_attack.py <id> --in FILE --json     # the file/JSON form
tools/crypto/xorshift128.py --outs --predict [--selftest]  # standalone
```

## The library modules — NOT CLIs

```python
from tools.crypto import lcg, lfsr, mt19937, xorshift128
```

These have no `__main__` — import them; `python3 tools/crypto/lcg.py` is
not a valid invocation.

## The pick rule

- `m` known → `lcg-recover`; not → `lcg-unknown-modulus`; `a,c,m`+high →
  `lcg-truncated`.
- taps known → `lfsr-predict`; else `berlekamp-massey`→`lfsr-recover`.
- 624 words → `mt19937-clone`; 4 → `xorshift128`; small seed → search.
