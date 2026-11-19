# CTR / stream nonce reuse — keystream recovery — summary

CTR and stream ciphers are XOR with a keystream: reuse a nonce and the keystream repeats. XOR the two ciphertexts — the keystream cancels and you hold P1 XOR P2, crib-draggable.

## Signal → route

- Two ciphertexts share a nonce/IV/counter → crib-drag
- Fixed IV in source, or nonce = message counter that wraps → collect pairs
- Known plaintext anywhere in one message → XOR onto the other ciphertext

## Falsifier

Falsifier — every pair uses a distinct nonce and no known plaintext exists: no two-message keystream is ever produced. Reclassify toward PRNG weaknesses in the keystream source instead.
