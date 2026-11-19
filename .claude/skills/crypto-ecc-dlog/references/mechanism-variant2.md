# Mechanism variant 2 — the attacks restated by what they exploit

## The nonce attacks — exploit `k` mistakes

| Attack | Exploits |
|---|---|
| `ecdsa-nonce-reuse` | `k_i == k_j` — same nonce, two equations |
| `hnp-ecdsa` | `k_i < B` — bounded nonce, lattice |
| `hnp` | `k_i` partially known — `(t,u)` leak, lattice |

## The dlog attacks — exploit group structure

| Attack | Exploits |
|---|---|
| `pohlig-hellman` | `ord` smooth — CRT-split dlog |
| `bsgs` | `x`/ord bounded — √(ord) time-memory |
| `smoothness` | the gate — `ord` factor size |

## The defect attacks — exploit the curve

| Attack | Exploits |
|---|---|
| `smart_attack` | `#E == p` — p-adic lift makes dlog a division |
| `singular_ec` | `Δ == 0` — iso to `G_m`/`G_a` |
| invalid curve | unvalidated `P` — off-curve smooth subgroups |

## The shared shape

Every attack reduces a hard problem to an easy one:
- reuse → two equations/one unknown.
- bias → lattice short-vector.
- smooth → small subgroup dlogs + CRT.
- bounded → √n collision.
- anomalous → p-adic division.
- singular → field dlog.
- unvalidated → per-curve small dlogs + CRT.
