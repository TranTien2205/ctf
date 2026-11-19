# CTR / stream nonce reuse — keystream recovery — case catalogue

CTR and stream ciphers are XOR with a keystream: reuse a nonce and the keystream repeats. XOR the two ciphertexts — the keystream cancels and you hold P1 XOR P2, crib-draggable.

## Cases

| # | Shape | Distinguisher | Attack |
|---|---|---|---|
| 1 | Two ciphertexts share a nonce/IV/counter | keystream reused | crib-drag |
| 2 | Fixed IV in source, or nonce = message counter that wraps | reuse guaranteed | collect pairs |
| 3 | Known plaintext anywhere in one message | keystream segment recovered directly | XOR onto the other ciphertext |

## Falsifier

Falsifier — every pair uses a distinct nonce and no known plaintext exists: no two-message keystream is ever produced. Reclassify toward PRNG weaknesses in the keystream source instead.

## Coverage notes

- Counter-mode nonces often increment per BLOCK not per message — reuse is at the block level, pairs must align by absolute counter.
- Base64/hex mismatches: XOR raw bytes, not encodings.
- CTR with a random nonce per message still fails when the nonce space is tiny (2^16) — birthday collisions appear after ~300 messages.

## Cross-references

`crib-drag-deep.md` · `gcm-nonce-reuse.md` · `single-byte-xor.md`
