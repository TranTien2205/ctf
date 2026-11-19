# Theory variant 2 — the math by attack, compact

## ECDSA signature algebra

```
k random ∈ [1, n-1]   R = k·G   r = R.x mod n
s = (z + r·d)·k⁻¹ mod n
```

Reuse `k` → solve. Bound `k` → lattice. The whole nonce family lives here.

## The group dlog

`h = g^x mod p`. Generic cost √ord. `ord = ∏ qᵢ^eᵢ` smooth → per-`qᵢ` small
dlogs + CRT.

## The curve group

`E: y² = x³ + ax + b`, `Q = d·G`, `ord(G) = n | #E`, `#E ≈ p+1` (Hasse:
`|#E - p - 1| ≤ 2√p`).

- `#E == p` → trace `t = 1` → anomalous.
- `Δ = 4a³+27b² ≡ 0` → singular.
- `ord` smooth → PH on the curve.
- `x` bounded → BSGS on the curve.

## The lattices

`k_i ≡ t_i·d + u_i (mod n)`, `k_i < B` — hidden number `d`. `lll.py` finds
a short basis; `d` sits in the short vector.

## The isomorphisms

- anomalous → `Q_p` lift → `log_p` homomorphism.
- singular node → `G_m` (field dlog); cusp → `G_a` (additive, trivial).
- invalid curve → `E'` smooth subgroup — the oracle computes `d·P'` on `E'`.
