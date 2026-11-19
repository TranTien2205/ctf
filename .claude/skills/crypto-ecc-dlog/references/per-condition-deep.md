# Per-condition deep — the preconditions, annotated

## `ecdsa-nonce-reuse` — each condition with the check

| Condition | Check | If violated |
|---|---|---|
| `r_i == r_j` | `Counter(r)` | `hnp-ecdsa` if biased |
| `z` correct | `sha256(m)` → int, truncation | verify fails |
| `n` correct | published curve order | verify fails |

## `hnp-ecdsa` — each condition with the check

| Condition | Check | If violated |
|---|---|---|
| `r` distinct | dedupe | reuse pair → `ecdsa-nonce-reuse` |
| `m ≥ required_signatures` | `hnp.required_signatures` | gather more |
| `k_i < B` ∀i | bound from statement | widen `B`, prune outliers |
| `z` correct | same as above | verify fails |

## `hnp` — each condition

| Condition | Check | If violated |
|---|---|---|
| `t_i = s_i⁻¹r_i` | recompute | wrong lattice |
| `u_i = -s_i⁻¹z_i` | recompute | wrong lattice |
| arrays aligned | `len(t) == len(u)` | parse error |

## `pohlig-hellman` — each condition

| Condition | Check | If violated |
|---|---|---|
| `ord` smooth | `smoothness --n` | `bsgs`/defect |
| `h ∈ <g>` | `pow(h, ord, p) == 1` | solve in `<h>` subgroup |
| `order` correct | `ord(g)`, not `p` | wrong `x` |

## `bsgs` — each condition

| Condition | Check | If violated |
|---|---|---|
| `ord`/`B` ≤ 2⁴⁴ | `ord` count | PH/defect |
| `h ∈ <g>` | `pow` check | subgroup |

## `smart`/`singular`/invalid — each condition

| Condition | Check | If violated |
|---|---|---|
| `#E == p` | count | not anomalous |
| `Δ == 0` | `4a³+27b² mod p` | not singular |
| no validation | submit `P'` | impossible |
