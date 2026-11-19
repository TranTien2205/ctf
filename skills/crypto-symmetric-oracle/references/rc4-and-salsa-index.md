# RC4 biases and Salsa/ChaCha nonce reuse — index

Stream ciphers that are NOT CTR still obey the reuse rule — the keystream
depends on (key, nonce); reuse either one and crib-drag applies.

## Companions

- `rc4-and-salsa-deep.md` — boundary conditions and the failure shape
- `rc4-and-salsa-checklist.md` — the same content as an ordered checklist
- `rc4-and-salsa-map.md` — the lookup table alone
- `../field-notes.md` — where outcomes land
