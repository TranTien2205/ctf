# Mechanism deep 2 — the attacks' inner workings, annotated

## `ecdsa-nonce-reuse` — the algebra

```
s1 = (z1 + r·d)/k   s2 = (z2 + r·d)/k    (same k ⟹ same r)
s1 - s2 = (z1 - z2)/k   →   k = (z1 - z2)/(s1 - s2) mod n
d = (s1·k - z1)/r mod n
```

Two equations, two unknowns (`k`, `d`) — the reuse collapses the lattice
need entirely.

## `hnp-ecdsa`/`hnp` — the lattice

From `s_i = (z_i + r_i·d)/k_i`:  `k_i ≡ t_i·d + u_i (mod n)` with
`t_i = s_i⁻¹r_i`, `u_i = -s_i⁻¹z_i`. With `k_i < B` the `d` is the hidden
number; `lll.py` recovers a short vector carrying `d`.

## `pohlig-hellman` — the CRT

`ord = ∏ qᵢ^eᵢ`. For each `qᵢ^eᵢ`, `x mod qᵢ^eᵢ` comes from a small dlog
in the `qᵢ`-subgroup; CRT recombines.

## `bsgs` — the time-memory tradeoff

`x = i·m + j`, `m = ⌈√ord⌉`; baby steps `g^j` vs giant `h·g^(-i·m)` collide
at `x`.

## `smart` — the p-adic lift

`#E == p` lifts `E` to `Q_p`; the p-adic log map is a homomorphism making
the dlog a division.

## `singular` — the iso

`Δ == 0` — a node/cusp maps `E` onto `G_m`/`G_a`; the dlog becomes a field
dlog or a trivial additive problem.

## Invalid curve — the off-curve oracle

`P'` on `E'` (different `b`), `ord` smooth — the oracle computes `d·P'` on
`E'`; `d mod ord_i` leaks; CRT reassembles.
