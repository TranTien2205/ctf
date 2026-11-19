# Onboarding — crypto-ecc-dlog in 5 minutes

## What this class is

A CTF crypto challenge where the answer is a **scalar** — an ECDSA private
key `d`, a discrete log `x`, or a nonce `k` revealing `d`. The toolkit's
`crypto_attack.py` carries six attack ids; `tools/crypto/` carries the
curve/lattice/dlog machinery.

## The 6 attacks in one table

| Shape | Attack |
|---|---|
| two sigs, same `r` | `ecdsa-nonce-reuse` (closed form) |
| sigs, distinct `r`, `k < B` | `hnp-ecdsa` (lattice) |
| `(t,u)` pairs, `k < B` | `hnp` (raw lattice) |
| `h = g^x mod p`, `ord` smooth | `pohlig-hellman` |
| `x` bounded / `n` small | `bsgs` |
| `#E == p` / `Δ == 0` / unvalidated point | `smart_attack`/`singular_ec`/invalid-curve |

## The order of checks

1. `r` dedupe → `ecdsa-nonce-reuse`.
2. `smoothness --n <ord>` → `pohlig-hellman` vs `bsgs`.
3. `Δ`/`#E` → `singular_ec`/`smart_attack`.
4. nonce bound → `hnp-ecdsa`/`hnp`.
5. oracle validation → invalid curve.

## The verify

`x·G == Q`/`pow(g, x, p) == h` — always, before recording.

## The files

`detection*.md` read · `cipher-identification.md` discriminate ·
`payload-dictionary*.md` solve · `verify*.md` verify ·
`field-notes-index.md` record · `falsifiers*.md` stop.

## The honest status

**Catalogue** — no local solve yet; the corpus is the field procedure.
