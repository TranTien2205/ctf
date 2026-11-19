# Summary variant — by the read

## The `cipher_id`-equivalent reads

| The read | The family | The command |
|---|---|---|
| `r` dup | nonce | `ecdsa-nonce-reuse --sigs --order` |
| `k < B`, many sigs | nonce | `hnp-ecdsa --sigs --order --nonce-*` |
| `(t,u)` | nonce | `hnp --t --u --modulus --bound` |
| `ord` smooth | dlog | `pohlig-hellman --g --h --p --order` |
| `x` bounded | dlog | `bsgs --g --h --p --order` |
| `ord` ? | dlog | `smoothness --n` |
| `#E == p` | defect | `smart_attack.py` |
| `Δ == 0` | defect | `singular_ec.py` |
| unvalidated `P` | defect | `ec.py` + small-dlog + CRT |

## The verify read

`x·G == Q` (curves) · `pow(g, x, p) == h` (fields).

## The record read

`post-probe` → `../field-notes.md` → `classify_solve.py`/`attempts`.

## The honest status

Catalogue — no local solve.
