# CBC IV = key and related IV bugs — index

If the service reuses the key as the IV (or exposes it through the decrypt error channel), three chosen-ciphertext queries recover the key. Rarer than padding oracles but instant when it fires.

## Related modules

- `cbc-iv-equals-key-deep.md` — mechanism internals and boundary conditions
- `cbc-iv-equals-key-checklist.md` — the ordered operational steps
- `cbc-iv-equals-key-catalogue.md` — case enumeration

## Cross-references

`cbc-bitflip.md` · `cbc-padding-oracle.md`
