# `smoothness` — reference card

**Applies when:** any dlog where `ord(g)`/`p-1`/`#E` factorization is unknown.

**Command:** `crypto_attack.py smoothness --n n`

**Returns:** factorization + largest prime factor.

**Decides:** ≤ 2⁴⁰ largest → `pohlig-hellman`; else look elsewhere.

**Deep:** `smoothness-deep.md`.
