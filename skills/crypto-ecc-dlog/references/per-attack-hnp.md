# `hnp` — reference card

**Applies when:** `(t_i, u_i)` pairs with `k_i = t_i·d - u_i mod n`, `k_i < B`.

**Command:** `crypto_attack.py hnp --t t.json --u u.json --modulus n --bound B`

**Preconditions:** `t = s⁻¹r`, `u = -s⁻¹z` (mod `n`); enough pairs.

**Falsifier:** no `d` satisfying `d·G == Q` → wrong `B` or too few pairs.

**Verify:** `d·G == Q`.

**Deep:** `hnp-deep.md`.
