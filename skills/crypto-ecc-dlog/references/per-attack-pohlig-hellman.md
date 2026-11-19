# `pohlig-hellman` — reference card

**Applies when:** `h = g^x mod p`, `ord(g)` smooth — `smoothness --n` first.

**Command:** `crypto_attack.py pohlig-hellman --g g --h h --p p --order n`

**Preconditions:** largest factor of `ord(g)` ≤ ~2⁴⁰; `h ∈ <g>`.

**Falsifier:** largest factor too big → index calculus, not PH;
`g^x ≠ h` → wrong `order`.

**Verify:** `pow(g, x, p) == h`.

**Deep:** `pohlig-hellman-deep.md`.
