# Mechanism — the primitives under every attack in this class

## The ECDSA signature equation

```
s = k⁻¹ (z + d·r)  mod n
```

`k` the nonce, `d` the private key, `z` the message hash as integer,
`r = x(k·G) mod n`, `n` the group order. Everything in this class is an
attack on this equation:

- **Two sigs, same `k`** (same `r`): subtract the equations, `k` cancels —
  `d = (s₁k - z₁)/r` once `k = (z₁ - z₂)/(s₁ - s₂)`.
- **Biased `k`** (`0 ≤ k < B`): each sig is a linear equation in `d` with
  small unknown `k_i` — lattice finds the short vector.
- **Leaked bits of `k`** — direct Hidden Number Problem.

## The DLP family

`h = g^x mod p` or `Q = x·G`:

- `x` bounded → `bsgs`, O(√B) time/space.
- `ord(g)` smooth → `pohlig-hellman`, solve per prime factor then CRT.
- `ord(g)` large prime → generic √n — out of reach above ~2⁴⁴ for BSGS.

## The curve-defect family

- **Anomalous** `#E(Fp) = p` → `smart_attack.py` lifts to `Q_p`, division by `p`
  gives `x` in linear time.
- **Singular** `4a³ + 27b² ≡ 0` → `singular_ec.py` maps points to a finite
  field where dlog is standard.
- **Invalid curve** — server adds attacker point without on-curve check →
  recover `d mod ord(P)` per fake curve, CRT.

## The `z` boundary

`z` arrives as a hash — `tools/crypto_attack.py` wants the integer. The
`--sigs` JSON accepts `[r, s, z]` triples or `{"r","s","z"}` objects.

## The verify

`x·G == Q` or `g^x mod p == h` — `tools/crypto/ec.py` does point arithmetic
for curve cases; `pow(g, x, p)` for finite-field cases.
