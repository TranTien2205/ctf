# ECB cut-and-paste / block substitution — index

ECB blocks are independent: a ciphertext block decrypts the same wherever it sits. Forge a message by swapping, replaying, or re-ordering blocks — the standard target is role/admin fields in encrypted profiles.

## Related modules

- `ecb-cut-and-paste-deep.md` — mechanism internals and boundary conditions
- `ecb-cut-and-paste-variant.md` — when the surface shape changes
- `ecb-cut-and-paste-checklist.md` — the ordered operational steps
- `ecb-cut-and-paste-catalogue.md` — case enumeration

## Cross-references

`ecb-detection.md` · `ecb-byte-at-a-time.md` · `token-forgery-workflows.md`
