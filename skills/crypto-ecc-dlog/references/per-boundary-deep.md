# Per-boundary deep — the limits in full

## The signature-count boundary

`required_signatures(order_bits, nonce_bits) = ⌈2·order_bits/leaked_bits⌉`:

| `k` leak | sigs (256-bit curve) |
|---|---|
| `k < 2^128` (half) | ~4 |
| `k < 2^64` | ~8 |
| 8 bits leaked | ~64 |
| 4 bits leaked | ~128 |
| 1 bit leaked | ~512 — impractical |

Below count → underdetermined lattice → wrong `d` that fails verify.
At count → works; add 1–2 for margin.

## The `bsgs` ceiling

`max_table = 1<<22` ≈ 4M entries → `ord ≤ ~2^44`. Above that:

- `--order` may still be the *bound* not the full order (a bounded `x`).
- `pohlig-hellman` if order smooth.
- Defect curve if params are custom.
- Else: not solvable by this toolkit — record the falsifier.

## The PH largest-factor ceiling

Largest factor `q_max ≤ ~2⁴⁰` — above that the factor's internal BSGS
stalls. `smoothness` reports it; `p-1 = 2q` with `q ~2^255` is a dead end.

## The `hnp` bound tightness

`B` must cover *every* `k_i` — one `k_i ≥ B` poisons the lattice. Prune
sigs where `k` might exceed `B` (e.g. an outlier timestamp).

## The `z` bit-length edge

`z` is `order_bits` truncation — 256 for secp256k1/P-256, 384 for P-384,
521 for P-521 (padding semantics differ slightly — check the curve).
