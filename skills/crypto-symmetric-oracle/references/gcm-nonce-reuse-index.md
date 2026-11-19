# GCM nonce reuse — the forbidden attack — index

GCM reusing a nonce leaks the GHASH authentication subkey H: two tagged ciphertexts under one nonce let you forge tags for arbitrary new ciphertexts. tools/gcm_nonce.py runs the algebra.

## Related modules

- `gcm-nonce-reuse-deep.md` — mechanism internals and boundary conditions
- `gcm-nonce-reuse-variant.md` — when the surface shape changes
- `gcm-nonce-reuse-checklist.md` — the ordered operational steps
- `gcm-nonce-reuse-catalogue.md` — case enumeration

## Cross-references

`tools-gcm-nonce.md` · `ctr-nonce-reuse.md` · `mac-forgery.md`
