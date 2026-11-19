# Detection surface deep — the observable plane, annotated

## The signature surface

- `(r, s)` pairs — `r` is the `x`-coordinate of `k·G`; equal `r` ⟹ equal `k`.
- `z`/`m` — the signed digest or the message to hash.
- `n` — the subgroup order; the modulus for `s`.

## The dlog surface

- `h = g^x mod p` — the statement; `x` the target.
- `ord(g)` — the order `h` lives in; `smoothness` gates it.
- `x` bound — `bsgs` gate.

## The curve surface

- `p a b` — `y² = x³ + ax + b`; `Δ = 4a³+27b²`.
- `G`, `n` — generator + subgroup order.
- `Q = d·G` — the verify target.
- `#E` — the curve order; `== p` anomalous.

## The oracle surface

- `multiply(P)`/`sign(m)`/`decrypt` — the probeable behaviour.
- validation presence — the invalid-curve gate.

## The derived surface

- `z` — the hash-as-int.
- `t = s⁻¹r`, `u = -s⁻¹z` — the `hnp` inputs.
- `ord(g)`, `#E`, `Δ` — the computed gates.
