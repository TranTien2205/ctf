# Summary deep — the whole class on one page

## What this class is

Recover a scalar — an ECDSA `d`, a dlog `x`, or a nonce `k` revealing `d` —
from a handout of curve params, signature pairs, a dlog statement, or a
signing/point oracle. Six attack ids in `crypto_attack.py`, six support
modules in `tools/crypto/`.

## The three families

- **Nonce** — `r` dup → `ecdsa-nonce-reuse`; `k < B` → `hnp-ecdsa`;
  `(t,u)` → `hnp`.
- **Dlog** — `ord` smooth → `pohlig-hellman`; `x` bounded → `bsgs`;
  `ord` unknown → `smoothness`.
- **Defect** — `Δ == 0` → `singular_ec`; `#E == p` → `smart_attack`;
  unvalidated point → invalid curve.

## The gates (free first)

`r` dedupe → `smoothness --n ord` → `Δ`/`#E` → `required_signatures` →
validation.

## The verify

`x·G == Q` or `pow(g, x, p) == h` — the only finish line; a scalar that
doesn't reproduce the public key isn't the key.

## The boundary

`bsgs` ≤ 2⁴⁴ · PH largest factor ≤ 2⁴⁰ · `m ≥ 2·order_bits/leaked_bits` ·
`Δ` exact-zero · `#E` exact-`p` · `B` covers all `k_i`.

## The record

`post-probe` (evidence ⊆ response) → `../field-notes.md` → `classify_solve.py`
or `knowledge/attempts/` falsifier → `decide.py` escalation rungs.

## The honest status

**Catalogue** — no local solve; the corpus is the field procedure.
