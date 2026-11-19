# Field manual — the 10-minute reference card

## The group first

`p`/`a`/`b`/`G`/`n` or curve name. `order` is always `n` (subgroup), never `p`.

## The signature inventory

Dedupe `r`. Count sigs vs `required_signatures(order_bits, nonce_bits)`.

## The decision

| If | Run |
|---|---|
| `r` repeats | `ecdsa-nonce-reuse --sigs f --order n` |
| `k < B` many sigs | `hnp-ecdsa --sigs f --order n --nonce-bits B` |
| `(t,u)` pairs | `hnp --t f --u f --modulus n --bound B` |
| `ord` smooth | `pohlig-hellman --g --h --p --order n` |
| `x` bounded | `bsgs --g --h --p --order n` |
| `#E == p` | `smart_attack.py` |
| `Δ == 0` | `singular_ec.py` |
| unvalidated point oracle | invalid curve (`ec.py`) |

## The flags

- `--sigs` — JSON file, `[r,s,z]` or `{"r","s","z"}`.
- `--order` — `n`, always.
- `--nonce-bits B` — `k < 2^B`.
- `--nonce-bound B` — `k < B`.
- `--t`/`--u` — JSON int lists.
- `--bound` — integer bound.

## The verify

`x·G == Q` / `pow(g, x, p) == h` — always.

## The falsifiers

No dup `r` / `d·G ≠ Q` / `ord` too big / `#E ≠ p` / `Δ ≠ 0` / validation.

## The record

`post-probe` + `../field-notes.md` + `classify_solve.py` / `knowledge/attempts/`.
