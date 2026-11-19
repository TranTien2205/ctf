# CBC-MAC and MAC-construction flaws — index

CBC-MAC is secure for fixed-length messages and forgeable for variable-length ones. A CTF classic: given MAC(m), produce MAC(m || m' ) without the key.

## Related modules

- `cbc-mac-deep.md` — mechanism internals and boundary conditions
- `cbc-mac-checklist.md` — the ordered operational steps
- `cbc-mac-catalogue.md` — case enumeration

## Cross-references

`mac-forgery.md` · `length-extension.md`
