# Curve-defect family — when the curve itself is the bug

## The three defects

| Defect | Check | Tool |
|---|---|---|
| anomalous `#E == p` | count points | `tools/crypto/smart_attack.py` |
| singular `Δ == 0` | `4a³+27b² mod p` | `tools/crypto/singular_ec.py` |
| invalid curve | server skips validation | `tools/crypto/ec.py` + small-dlog |

## The check order

1. `Δ = -16(4a³ + 27b²) mod p` — `0` → `singular_ec` (trivial solve).
2. `#E` → `== p` → `smart_attack` (linear solve).
3. `#E` smooth → `pohlig-hellman` with `ec.py` point ops.
4. Server takes points → invalid curve.

## The non-defects

A *properly chosen* curve — `secp256k1`, P-256, Curve25519 — has none of
these. If the handout names a real curve, the bug is in the nonce or the
protocol, not the curve.

## The `ec.py` toolbox

`ec.curve(name_or_params)` → add/mul on custom `(p, a, b)`. Use it to
construct fake curves (invalid-curve attack), verify `x·P == Q`, and
decompress points.

## The pairing case (out of reach)

MOV/Frey-Rück on small embedding degree — no pairing tool in this tree.
If the shape appears, record it as an intended-path note; it needs
`sage`/`PBC` (absent).
