# Per-condition — the named preconditions per attack

## `ecdsa-nonce-reuse` conditions

- `r_i == r_j` byte-identical for some pair.
- `z_i`, `z_j` correct per message.
- `n` correct.

## `hnp-ecdsa` conditions

- `r_i` all distinct.
- `0 ≤ k_i < B` uniform across sigs.
- `m ≥ required_signatures`.
- `n` correct.

## `hnp` conditions

- `(t_i, u_i)` aligned parallel arrays.
- `t_i = s_i⁻¹r_i mod n`, `u_i = -s_i⁻¹z_i mod n` correct.
- `k_i < B` uniform.

## `pohlig-hellman` conditions

- `ord(g)` fully factored, largest factor ≤ ~2⁴⁰.
- `h ∈ <g>`.

## `bsgs` conditions

- `ord(g)` or `x`-bound ≤ ~2⁴⁴.
- `h ∈ <g>`.

## `smart_attack` conditions

- `p` prime.
- `Δ ≠ 0` (nonsingular).
- `#E(Fp) == p` exactly.

## `singular_ec` conditions

- `Δ ≡ 0 mod p`.
- `P`, `Q` nonsingular.

## Invalid curve conditions

- Server accepts arbitrary `P` without `on_curve` check.
- `E'_i` orders cover `n` via CRT.

## The verify condition

Whatever the route, `x·G == Q`/`g^x == h` must hold.
