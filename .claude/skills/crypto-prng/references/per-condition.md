# Per-condition — every requirement → the check → the files

## The nonce-independent conditions (PRNG's own)

| Condition | Check | Files |
|---|---|---|
| generator named | fingerprint | `detection-deep.md` |
| count met | `len` floor | `per-check*.md` |
| raw+consecutive | normalize | `edge-cases*.md` |
| params known | `m`/`a`/`c`/taps | `preconditions*.md` |

## The per-attack conditions

| Attack | Condition | Files |
|---|---|---|
| `lcg-recover` | `m` known, 3 outs | `per-attack-lcg-recover.md` |
| `lcg-unknown-modulus` | 6 outs | `per-attack-*.md` |
| `lcg-truncated` | `m`,`a`,`c`, `--low-bits` | `per-attack-*.md` |
| `berlekamp-massey` | 2·w bits | `per-attack-*.md` |
| `lfsr-predict` | taps+width | `per-attack-*.md` |
| `mt19937-clone` | 624 words | `per-attack-*.md` |
| `xorshift128` | 4 outs | `per-attack-*.md` |
| seed | bounded window | `per-family-seed.md` |

## The meta conditions

| Condition | Files |
|---|---|
| `predict==held-back` before record | `verify*.md`,`evidence*.md` |
| falsifier → `attempts` | `negative-results*.md` |
| `decide.py` rungs | `falsifiers*.md` |
