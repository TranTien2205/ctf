# CBC padding oracle — Vaudenay decryption — index

A service that answers 'padding valid' vs 'padding invalid' decrypts arbitrary ciphertext for you, one byte per ~256 requests. The error channel IS the exploit.

## Related modules

- `cbc-padding-oracle-deep.md` — mechanism internals and boundary conditions
- `cbc-padding-oracle-variant.md` — when the surface shape changes
- `cbc-padding-oracle-checklist.md` — the ordered operational steps
- `cbc-padding-oracle-catalogue.md` — case enumeration

## Cross-references

`tools-pad-oracle.md` · `response-distinguishers.md` · `cbc-bitflip.md`
