# Glossary deep — the terms, expanded

## The ECDSA terms

| Term | Definition | Where it matters |
|---|---|---|
| `k` | ephemeral nonce `k ∈ [1, n-1]` | every nonce attack targets it |
| `r` | `x(k·G) mod n` | identical `r` = identical `k` |
| `s` | `k⁻¹(z + d·r) mod n` | the equation to exploit |
| `z` | `int(H(m))` truncated to `order_bits` | wrong `z` → wrong `d` |
| `d` | private scalar | the deliverable |
| `Q` | `d·G` public key | the verify target |
| `n` | subgroup order `ord(G)` | `--order`, always `n` not `p` |

## The DLP terms

| Term | Definition | Where it matters |
|---|---|---|
| `g` | generator of `Fp*` subgroup | `h = g^x` |
| `h` | `g^x` — the statement | the target |
| `x` | discrete log | the deliverable |
| `ord(g)` | subgroup order | PH/BSGS bound |
| `p-1` | full group order | smoothness input |
| smooth | all factors small | PH applicability |
| safe prime | `p-1 = 2q` | designed-resistant |

## The curve terms

| Term | Definition | Where it matters |
|---|---|---|
| `E(Fp)` | `y² = x³ + ax + b` over `Fp` | the object |
| `#E` | point count `p+1-t` | `== p` → smart |
| `t` | trace `p+1-#E` | anomalous check |
| `Δ` | `-16(4a³+27b²)` | `==0` → singular |
| twist | `E'` sharing a coefficient | invalid-curve tool |
| embedding degree | smallest `k` with `n | p^k - 1` | MOV attack |

## The lattice terms

| Term | Definition | Where it matters |
|---|---|---|
| HNP | `k_i = t_i·d - u_i mod n`, `k_i < B` | the problem |
| `(t,u)` | `t = s⁻¹r`, `u = -s⁻¹z` | the transform |
| `B` | bound on `k` | `--nonce-bits`/`--bound` |
| `m` | signature count | `required_signatures` |
| LLL | basis reduction | `tools/crypto/lll.py` |
