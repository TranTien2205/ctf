# Glossary variant — the terms by family, compact

## Nonce terms

- **nonce `k`** — the per-signature ephemeral scalar.
- **`r`** — `R.x mod n` where `R = k·G` — identifies `k`.
- **`s`** — the signature scalar `s = (z + r·d)k⁻¹`.
- **`z`** — `int(H(m))` truncated/`mod n`.
- **`t`, `u`** — the `hnp` pair `t = s⁻¹r`, `u = -s⁻¹z`.
- **`B`** — the nonce bound.
- **`required_signatures`** — the count heuristic for the lattice.

## Dlog terms

- **`h = g^x`** — the dlog statement.
- **`ord(g)`/`ord`** — the subgroup order.
- **smooth** — largest prime factor small enough for PH.
- **safe prime** — `p = 2q+1` — kills PH.
- **CRT** — recombines `x mod qᵢ^eᵢ`.

## Curve terms

- **`E: y² = x³+ax+b`** — short Weierstrass.
- **`Δ = 4a³+27b²`** — discriminant; `0` → singular.
- **`#E`** — curve order; `== p` → anomalous.
- **`n`** — `ord(G)` — the `--order`.
- **`d·G == Q`** — the verify.
- **MOV/Frey-Rück** — pairing reduction; not tooled here.

## Meta terms

- **class/impact** — the evidence kinds.
- **falsifier** — the kill condition.
- **chain card** — the recorded solve.
