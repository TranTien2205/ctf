# Mechanism deep — the internals the tools implement

## `hnp.ecdsa_recover_nonce_reuse`

```
k = (z₁ - z₂) · (s₁ - s₂)⁻¹ mod n
d = (s₁·k - z₁) · r⁻¹ mod n
```

Input `{"r","s","z"}` per sig; first two entries used.

## `hnp.ecdsa_recover_biased_nonce`

Per sig `i`: `k_i = s_i⁻¹z_i + s_i⁻¹r_i·d mod n`, `k_i < B`. Builds the
`(m+1)`-dim lattice `L` with rows `(n,0,…)`, `(t_i,0,…,B/n)`, reduces with
`lll.lll_reduce`, reads the candidate `d` off the last coordinate of the
short vector, then `d·G == Q` when `--curve`/`--pubkey` given.

## `dlog.pohlig_hellman`

For `ord(g) = Π q_i^{e_i}`:

1. `x mod q_i` — write `x = Σ x_j q^j` digits; each digit via a `q`-size BSGS
   on `h^{n/q^{j+1}}`.
2. CRT the residues mod `q_i^{e_i}` → `x mod ord(g)`.

The tool computes `ord(g)` first — a non-generator `g` doesn't yield a wrong
coset.

## `dlog.bsgs`

`x = i·m + j`, `m = ⌈√n⌉`: table `j → g·g^j`, then `h·g^{-im}` lookups.
`max_table` default `1 << 22`.

## `smart_attack`

Lift `P, Q` to `P', Q'` on `E(Q_p)`. p-adic log `λ(P') ∈ p·Q_p`; ratio
`λ(Q')/λ(P')` = `x mod p`. Linear time — `O(log p)`.

## `singular_ec`

- **Cusp** — `x ↦ slope(P) = (x - x_s)/y` isomorphism to `Fp+`; `x = slope(Q)/slope(P) mod p`.
- **Node** — `Fp*` (or `Fp²*`) isomorphism; standard dlog follows.

## `ec.curve`

`ec.curve("secp256k1")` or `ec.curve({"p","a","b"})` → `add`, `mul`,
`point`, `order` (small `p`). Invalid-curve construction + verify.
