# Theory deep — the full math layer

## The ECDSA signature equation, fully

```
(r, s):  R = k·G,  r = x(R) mod n
         s = k⁻¹ (z + d·r) mod n
```

`k` is the whole security. Leak it, repeat it, bound it — `d` falls.

### Reuse

Same `k` → same `r`. Two sigs:

```
s₁ - s₂ = k⁻¹ (z₁ - z₂)  mod n
k       = (z₁ - z₂)(s₁ - s₂)⁻¹  mod n
d       = (s₁k - z₁) r⁻¹  mod n
```

### Bias → HNP

`k_i < B` for all `i`: `k_i = s_i⁻¹z_i + s_i⁻¹r_i·d = t_i·d - u_i` (mod n)
with `t_i = s_i⁻¹r_i`, `u_i = -s_i⁻¹z_i`. The vector
`(k_1,…,k_m, B·d/n)` is short in the lattice — LLL finds it. Minimum
signatures: `m ≥ order_bits / log2(n/B)` (the `required_signatures` formula).

### Deterministic `k` (RFC 6979)

`k = HMAC(d, m)` — identical input → identical `(r, s)`. Reuse only happens
across *different* messages with broken RNG — RFC 6979 isn't the bug, it's
what makes reuse *impossible* when implemented right.

## The DLP bounds

`O(√n)` generic (BSGS, Pollard-rho). On a curve `n ≈ p`, so `O(√p)`.
Pohlig-Hellman: `O(√q_max)` where `q_max` is the largest factor of `ord(g)`.

## The curve defects

- **Anomalous `#E = p`**: lift to `E(Q_p)` — the p-adic log of `x·P` and `Q`
  in `p·Q_p` gives `x` by division. `O(log p)`.
- **Singular `Δ = 0`**: parameterize by the singular point's tangent —
  isomorphism to `Fp+` (cusp → linear `x = slope(Q)/slope(P)`) or `Fp*`
  (node → standard dlog, PH if `p-1` smooth).
- **Invalid**: attacker `P' ∈ E'` with `ord(P')` smooth — `d mod ord(P')`
  per curve, CRT to `d`.

## The lattice machinery

`lll.py` is pure-python LLL (no `fpylll` here). Dimension `m+1` — keep `m`
near the minimum; ~40 dims is the practical ceiling in pure python.
