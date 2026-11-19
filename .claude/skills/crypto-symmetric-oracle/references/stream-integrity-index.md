# Stream/CTR integrity — malleability — index

CTR/stream ciphertext is malleable per-bit: flip a ciphertext bit and the same plaintext bit flips. No integrity means you own the plaintext.

## Related modules

- `stream-integrity-deep.md` — mechanism internals and boundary conditions
- `stream-integrity-checklist.md` — the ordered operational steps
- `stream-integrity-catalogue.md` — case enumeration

## Cross-references

`ctr-nonce-reuse.md` · `cbc-bitflip.md` · `token-forgery-workflows.md`
