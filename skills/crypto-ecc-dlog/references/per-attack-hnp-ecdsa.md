# `hnp-ecdsa` — reference card

**Applies when:** many sigs, distinct `r`, bounded `k` (`--nonce-bits` or
`--nonce-bound`).

**Command:** `crypto_attack.py hnp-ecdsa --sigs sigs.json --order n --nonce-bits B`

**Preconditions:** sig count ≥ `required_signatures`, all `r` distinct, `B`
covers `k`.

**Falsifier:** `d·G ≠ Q` → too few sigs / wrong `B` / nonces unbiased.

**Verify:** `d·G == Q` (`--curve`/`--pubkey` verify inside).

**Deep:** `hnp-ecdsa-deep.md`.
