# CTR / stream nonce reuse — keystream recovery — index

CTR and stream ciphers are XOR with a keystream: reuse a nonce and the keystream repeats. XOR the two ciphertexts — the keystream cancels and you hold P1 XOR P2, crib-draggable.

## Related modules

- `ctr-nonce-reuse-deep.md` — mechanism internals and boundary conditions
- `ctr-nonce-reuse-variant.md` — when the surface shape changes
- `ctr-nonce-reuse-checklist.md` — the ordered operational steps
- `ctr-nonce-reuse-catalogue.md` — case enumeration

## Cross-references

`crib-drag-deep.md` · `gcm-nonce-reuse.md` · `single-byte-xor.md`
