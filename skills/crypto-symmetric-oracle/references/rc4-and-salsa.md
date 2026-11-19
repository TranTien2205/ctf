# RC4 biases and Salsa/ChaCha nonce reuse

Stream ciphers that are NOT CTR still obey the reuse rule — the keystream
depends on (key, nonce); reuse either one and crib-drag applies.

## RC4

| Weakness | Shape | Use |
|---|---|---|
| Key-scheduling bias | early keystream bytes skew to the key | mostly academic in CTF |
| Invariance / single-byte bias | 'Z' byte 2 biases to 0 | statistical; needs MANY samples |
| Same key, no nonce | every message same keystream | crib-drag directly |

RC4 in CTF is almost always 'same keystream twice' — skip the bias math,
XOR the ciphertexts.

## Salsa20 / ChaCha (unauthenticated)

- `ChaCha20` alone (no Poly1305): XOR keystream, same rules as CTR.
- Nonce misuse: `ctr-nonce-reuse.md` + `crib-drag.md`.
- `ChaCha20-Poly1305`: authenticated — boundary rules apply.

## Detection

- Ciphertext length == plaintext length: stream mode.
- 8-byte or 12-byte nonce field next to ciphertext: Salsa/ChaCha family.
- `Salsa20`, `ChaCha20`, `XSalsa20` in source: confirms the family.

## The attack order

1. Nonce reuse? → crib-drag.
2. Weak seed/nonce = timestamp? → seed-search (`../crypto-prng/`).
3. Authenticated variant? → class boundary.
