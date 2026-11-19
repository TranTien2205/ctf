# Theory — the math that makes the attacks work

## ECDSA

Sign: `k ← random`, `r = x(k·G) mod n`, `s = k⁻¹(z + d·r) mod n`.
Verify: `s⁻¹z·G + s⁻¹r·Q` has `x == r`.

Every attack below exploits a leak on `k` or `d`:

| Leak | Result |
|---|---|
| same `k` twice | `k`, then `d` — closed form |
| `k < B` small | `d` via lattice — `hnp-ecdsa` |
| bits of `k` | `d` via `hnp` |
| `d` bits | `d` directly |

## DLP

`h = g^x mod p` — `x` is the discrete log. Generic bound `O(√n)`; sub-generic
on smooth `ord(g)` (PH) or bounded `x` (BSGS); index calculus below that
for large `p` (out of scope).

## The curve structures

- `E(Fp)` order `#E = p + 1 - t` (Hasse: `|t| ≤ 2√p`).
- `#E == p` → anomalous → `smart_attack` in `O(log p)`.
- `Δ = -16(4a³+27b²) ≡ 0` → singular → `singular_ec` maps to `Fp+`/`Fp*`.
- Small embedding degree → MOV/Frey-Rück to `F_{p^k}` (pairing tools absent
  here — flag it and move on if it appears).

## The lattice view

HNP: `k_i = t_i·d - u_i mod n`, `k_i < B` → the vector `(k_1,…,k_m)` is
unusually short in the lattice → `lll.py` finds it → `d` falls out. The
bound `B` and count `m` are the whole game — `required_signatures` gives the
minimum `m` for `B`.

## Why verify is mandatory

Every attack here is a *candidate-generator*: reuse gives one `d`, HNP
gives a few candidates, PH/BSGS give one `x`. Only `x·G == Q` distinguishes
"the algebra was right" from "the input was wrong".
