# RC4 biases and Salsa/ChaCha nonce reuse — checklist

Stream ciphers that are NOT CTR still obey the reuse rule — the keystream
depends on (key, nonce); reuse either one and crib-drag applies.

## Checklist

- [ ] `ChaCha20` alone (no Poly1305): XOR keystream, same rules as CTR.
- [ ] Nonce misuse: `ctr-nonce-reuse.md` + `crib-drag.md`.
- [ ] `ChaCha20-Poly1305`: authenticated — boundary rules apply.

## Falsifier

Stop when the module's abort conditions fire — recorded as a negative, not retried as a variant.
