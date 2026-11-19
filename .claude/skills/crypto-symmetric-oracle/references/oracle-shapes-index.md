# Oracle shapes — the four you can hold — index

An oracle is any endpoint that answers a question about a ciphertext, a plaintext, or a tag. Before any exploit loop, name exactly which one you hold — encrypt, decrypt, padding-check, or verify — because the attack inventory differs completely per shape.

## Related modules

- `oracle-shapes-deep.md` — mechanism internals and boundary conditions
- `oracle-shapes-variant.md` — when the surface shape changes
- `oracle-shapes-checklist.md` — the ordered operational steps
- `oracle-shapes-catalogue.md` — case enumeration

## Cross-references

`ecb-detection.md` · `cbc-padding-oracle.md` · `ctr-nonce-reuse.md` · `mac-forgery.md` · `../field-notes.md`
