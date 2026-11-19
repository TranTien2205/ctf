# `smart_attack` — reference card

**Applies when:** custom curve `y² = x³ + ax + b / Fp` with `#E(Fp) == p`.

**Tool:** `tools/crypto/smart_attack.py` (module + `--selftest`).

**Preconditions:** `p` prime, `Δ ≠ 0`, `#E == p` exactly.

**Falsifier:** `x·P ≠ Q` → not anomalous → `pohlig-hellman`/`singular_ec`.

**Verify:** `x·P == Q`.

**Deep:** `smart-attack-deep.md`.
