# Preconditions deep — every condition with the check

## `ecdsa-nonce-reuse` preconditions

| Condition | Check | If violated |
|---|---|---|
| ≥2 sigs | count | dead on nonce alone |
| `r_i == r_j` | `Counter(r)` | `hnp-ecdsa` |
| `z` per sig | `int(H(m))` trunc | verify fails |
| `n` correct | published `ord(G)` | verify fails |

## `hnp-ecdsa` preconditions

| Condition | Check | If violated |
|---|---|---|
| all `r` distinct | dedupe | pair → reuse |
| `m ≥ required` | `required_signatures` | gather more |
| `k_i < B` ∀i | bound from statement | widen `B`, prune |
| `B` correct | `--nonce-bits`/`--nonce-bound` | wrong lattice |

## `hnp` preconditions

| Condition | Check | If violated |
|---|---|---|
| `(t,u)` aligned | `len(t) == len(u)` | parse error |
| `t = s⁻¹r`, `u = -s⁻¹z` | recompute mod `n` | wrong lattice |
| `k_i < B` ∀i | bound | outlier poisons |

## `pohlig-hellman` preconditions

| Condition | Check | If violated |
|---|---|---|
| `ord` smooth | `smoothness --n` | `bsgs`/defect |
| `h ∈ <g>` | `pow(h, ord, p) == 1` | subgroup solve |
| `ord` correct | `ord(g)` | wrong `x` |

## `bsgs` preconditions

| Condition | Check | If violated |
|---|---|---|
| `ord`/`B` ≤ 2⁴⁴ | count | PH/defect |
| `h ∈ <g>` | `pow` | subgroup |

## `smart`/`singular`/invalid preconditions

| Condition | Check | If violated |
|---|---|---|
| `#E == p` | count | not anomalous |
| `Δ == 0` | `4a³+27b² mod p` | not singular |
| `P`, `Q` nonsingular | — | wrong iso |
| no validation | submit `P'` | impossible |
