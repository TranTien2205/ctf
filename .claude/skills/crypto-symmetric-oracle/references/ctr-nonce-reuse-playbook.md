# CTR / stream nonce reuse — keystream recovery — playbook

CTR and stream ciphers are XOR with a keystream: reuse a nonce and the keystream repeats. XOR the two ciphertexts — the keystream cancels and you hold P1 XOR P2, crib-draggable.

## Ordered playbook

1. Collect ciphertext pairs sharing a nonce (grep the handout or request duplicates).
2. XOR them: K_xor = C1 XOR C2 = P1 XOR P2.
3. Run crib-drag: python3 tools/crypto_attack.py crib-drag --ct1 <h1> --ct2 <h2> --crib 'flag{' — slide the crib across every offset.
4. If you know a whole plaintext block, XOR it directly with its ciphertext to get raw keystream, then XOR onto any same-nonce ciphertext.
5. A third ciphertext under the same nonce lets you cross-check candidate plaintexts character by character.

## Falsifier

Falsifier — every pair uses a distinct nonce and no known plaintext exists: no two-message keystream is ever produced. Reclassify toward PRNG weaknesses in the keystream source instead.

## Commands

```bash
python3 tools/crypto_attack.py crib-drag --ct1 <h1> --ct2 <h2> --crib 'flag{'
python3 tools/crypto_attack.py crib-drag --ct1 <h1> --ct2 <h2> --crib 'Content-Type'
```
