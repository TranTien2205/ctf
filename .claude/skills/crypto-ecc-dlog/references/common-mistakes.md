# Common mistakes — the traps that cost time

## Detection mistakes

- **Similar `r` ≠ same `r`** — reuse means byte-identical `r`; a "close" `r`
  is not reuse, it's the biased case (`hnp-ecdsa`).
- **One signature, many attempts** — a single sig carries no nonce info;
  you need ≥2, or the oracle.
- **`p` vs `n` swapped** — `--order` is `n` (subgroup order), never `p`.
- **Skipping `smoothness`** — running `bsgs` on a 200-bit order is a stall.

## Math mistakes

- **Wrong `z`** — hash truncates to `order_bits` (FIPS), not `mod n`. If the
  verify fails, try the other convention.
- **`s⁻¹` in the wrong field** — all ECDSA arithmetic is `mod n`, not `mod p`.
- **`t`/`u` swapped** in `hnp` — `t = s⁻¹r`, `u = -s⁻¹z` (mod `n`).
- **CRT on non-coprime factors** — `ord(g)` factors must be the *prime-power*
  components `q_i^{e_i}` for PH/CRT.

## Curve mistakes

- **Anomalous ≠ "prime order"** — `#E == p` is broken (smart_attack); `#E`
  being prime is *good* crypto.
- **`Δ == 0` check on `mod p`** — the discriminant is modular, not integer.
- **Expecting `bsgs` on `Q = x·G`** — `dlog.bsgs` is for `g^x mod p`; on
  curves you need point ops (`ec.py`) — the bound logic is the same but
  the arithmetic isn't.

## Evidence mistakes

- Claiming a flag from a scalar that never passed `x·G == Q`.
- Trusting a `crypto_attack.py` result without reading the verify step —
  the tools report candidates; the public-key check decides.
