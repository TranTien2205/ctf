# Preconditions — what must be true before each attack

## `ecdsa-nonce-reuse`

- ≥2 signatures, identical `r`.
- `z` correct per signature.
- `--order` = `n`.

## `hnp-ecdsa`

- All `r` distinct.
- `0 ≤ k < B` for every sig, `B` known/inferable.
- sig count ≥ `required_signatures(order_bits, nonce_bits)`.
- `--curve`/`--pubkey` to self-verify.

## `hnp`

- `(t_i, u_i)` pairs aligned, same length.
- `t = s⁻¹r`, `u = -s⁻¹z mod n`.
- `--bound` = integer `B`.

## `pohlig-hellman`

- `ord(g)` smooth — `smoothness` gate passed.
- `h ∈ <g>` — `pow(h, order, p) == 1`.
- `--order` = `ord(g)`, not `p`.

## `bsgs`

- `ord(g)` or bound ≤ ~2⁴⁴.
- `h ∈ <g>`.

## `smart_attack`

- `p` prime, `Δ ≠ 0`, `#E == p`.

## `singular_ec`

- `Δ ≡ 0 mod p`; `P`, `Q` nonsingular.

## Invalid curve

- Server computes `d·P'` without on-curve check.
- Enough smooth-order `E'_i` to cover `n` via CRT.
