# CTR / stream nonce reuse — keystream recovery — surface variants

CTR and stream ciphers are XOR with a keystream: reuse a nonce and the keystream repeats. XOR the two ciphertexts — the keystream cancels and you hold P1 XOR P2, crib-draggable.

## When the shape changes

| Variant | What changes | Route |
|---|---|---|
| Two ciphertexts share a nonce/IV/counter | keystream reused | crib-drag |
| Fixed IV in source, or nonce = message counter that wraps | reuse guaranteed | collect pairs |
| Known plaintext anywhere in one message | keystream segment recovered directly | XOR onto the other ciphertext |

## Variant-specific traps

- Counter-mode nonces often increment per BLOCK not per message — reuse is at the block level, pairs must align by absolute counter.
- Base64/hex mismatches: XOR raw bytes, not encodings.
- CTR with a random nonce per message still fails when the nonce space is tiny (2^16) — birthday collisions appear after ~300 messages.

## Falsifier

Falsifier — every pair uses a distinct nonce and no known plaintext exists: no two-message keystream is ever produced. Reclassify toward PRNG weaknesses in the keystream source instead.

## Cross-references

`crib-drag-deep.md` · `gcm-nonce-reuse.md` · `single-byte-xor.md`
