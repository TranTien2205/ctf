# `bsgs` — reference card

**Applies when:** `x` bounded or `ord(g)` ≤ ~2⁴⁴.

**Command:** `crypto_attack.py bsgs --g g --h h --p p --order n`

**Preconditions:** `√ord(g)` fits memory; `h ∈ <g>`.

**Falsifier:** no collision → `x` outside bound or `h` outside `<g>`.

**Verify:** `pow(g, x, p) == h`.

**Deep:** `bsgs-deep.md`.
