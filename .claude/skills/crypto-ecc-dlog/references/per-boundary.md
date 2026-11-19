# Per-boundary — the numeric limits, indexed

## Signature counts

- `ecdsa-nonce-reuse`: exactly 2 (the reuse pair).
- `hnp-ecdsa`: `required_signatures(order_bits, nonce_bits)` ≈
  `2·order_bits/leaked_bits`.
- `hnp`: same count formula.

## Order ceilings

| Attack | Ceiling |
|---|---|
| `bsgs` | `ord`/`B` ≤ ~2⁴⁴ |
| `pohlig-hellman` | largest factor ≤ ~2⁴⁰ |
| `hnp-ecdsa`/`hnp` | bound `B < n`; sigs ≥ count formula |
| `ecdsa-nonce-reuse` | none — closed form |
| `smart_attack` | `p` size no limit — linear in `log p` |
| `singular_ec` | `p-1` smooth for node case |

## The `z` bits

`z` truncated to `order_bits` (≤ 256 bits for secp256k1/P-256) — not `mod n`
unless the challenge uses the variant.

## The `--nonce-bits`/`--nonce-bound` relation

`--nonce-bits B` = `k < 2^B`; `--nonce-bound B` = `k < B`. Equivalent —
pick whichever the challenge statement gives.

## The curve-field split

- `Q = x·P` → `ec.py` point ops; `x` bounded by `ord(P)`.
- `h = g^x mod p` → `dlog.py`; `x` bounded by `ord(g)`.
