# `singular_ec` — reference card

**Applies when:** `Δ = -16(4a³+27b²) ≡ 0 mod p` — the curve is singular.

**Tool:** `tools/crypto/singular_ec.py` (module + `--selftest`).

**Preconditions:** `P`, `Q` are nonsingular points; for the node case,
`p-1` smooth helps.

**Falsifier:** `x·P ≠ Q` → wrong singularity type / not singular.

**Verify:** `x·P == Q`.

**Deep:** `singular-ec-deep.md`.
