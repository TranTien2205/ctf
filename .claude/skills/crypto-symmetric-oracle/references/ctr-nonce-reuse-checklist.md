# CTR / stream nonce reuse — keystream recovery — operational checklist

CTR and stream ciphers are XOR with a keystream: reuse a nonce and the keystream repeats. XOR the two ciphertexts — the keystream cancels and you hold P1 XOR P2, crib-draggable.

## Checklist

- [ ] Collect ciphertext pairs sharing a nonce (grep the handout or request duplicates).
- [ ] XOR them: K_xor = C1 XOR C2 = P1 XOR P2.
- [ ] Run crib-drag: python3 tools/crypto_attack.py crib-drag --ct1 <h1> --ct2 <h2> --crib 'flag{' — slide the crib across every offset.
- [ ] If you know a whole plaintext block, XOR it directly with its ciphertext to get raw keystream, then XOR onto any same-nonce ciphertext.
- [ ] A third ciphertext under the same nonce lets you cross-check candidate plaintexts character by character.

## Abort conditions

- Counter-mode nonces often increment per BLOCK not per message — reuse is at the block level, pairs must align by absolute counter.
- Base64/hex mismatches: XOR raw bytes, not encodings.
- CTR with a random nonce per message still fails when the nonce space is tiny (2^16) — birthday collisions appear after ~300 messages.

## Falsifier

Falsifier — every pair uses a distinct nonce and no known plaintext exists: no two-message keystream is ever produced. Reclassify toward PRNG weaknesses in the keystream source instead.

## Cross-references

`crib-drag-deep.md` · `gcm-nonce-reuse.md` · `single-byte-xor.md`
