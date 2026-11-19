# tools/gcm_nonce.py — the forbidden attack driver — index

Recovers the GHASH subkey H from two nonce-reused records, then forges a tag for a chosen new ciphertext. Algebraic, deterministic — no oracle loop.

## Related modules

- `tools-gcm-nonce-deep.md` — mechanism internals and boundary conditions
- `tools-gcm-nonce-checklist.md` — the ordered operational steps
- `tools-gcm-nonce-catalogue.md` — case enumeration

## Cross-references

`gcm-nonce-reuse.md` · `ctr-nonce-reuse.md`
