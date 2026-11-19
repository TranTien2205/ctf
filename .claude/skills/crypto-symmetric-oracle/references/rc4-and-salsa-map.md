# RC4 biases and Salsa/ChaCha nonce reuse — map

| Weakness | Shape | Use |
|---|---|---|
| Key-scheduling bias | early keystream bytes skew to the key | mostly academic in CTF |
| Invariance / single-byte bias | 'Z' byte 2 biases to 0 | statistical; needs MANY samples |
| Same key, no nonce | every message same keystream | crib-drag directly |

Expanded rows and abort conditions: `rc4-and-salsa.md` and `rc4-and-salsa-deep.md`.
