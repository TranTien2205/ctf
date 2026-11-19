# Summary — crypto-ecc-dlog at a glance

## The class

Curve, nonce, or discrete-log recovery — the answer is a scalar `d`/`x`/`k`.
`crypto_attack.py` + `tools/crypto/` carry the machinery.

## The discriminator

| Observation | Attack |
|---|---|
| two sigs, same `r` | `ecdsa-nonce-reuse` |
| sigs, distinct `r`, `k < B` | `hnp-ecdsa` |
| `(t,u)` pairs | `hnp` |
| `ord` smooth | `pohlig-hellman` |
| `x` bounded | `bsgs` |
| `ord` unknown | `smoothness` |
| `#E == p` | `smart_attack` |
| `Δ == 0` | `singular_ec` |
| unvalidated point oracle | invalid curve |

## The procedure

`detection*.md` → `cipher-identification.md` → `payload-dictionary*.md` →
`verify*.md` → `field-notes-index.md`.

## The verify

`x·G == Q` or `pow(g, x, p) == h` — always.

## The honest status

**Catalogue** — no local solve.
