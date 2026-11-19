# `ecdsa-nonce-reuse` — reference card

**Applies when:** two signatures share an `r` value.

**Command:** `crypto_attack.py ecdsa-nonce-reuse --sigs sigs.json --order n`

**Preconditions:** ≥2 sigs, same `r`, correct `z`, correct `n`.

**Falsifier:** `d·G ≠ Q` after recovery → `r` not equal / `z` wrong.

**Verify:** `d·G == Q`.

**Deep:** `ecdsa-nonce-reuse-deep.md`.
