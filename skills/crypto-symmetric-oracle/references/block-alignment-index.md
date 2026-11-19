# Block alignment — prefix, suffix, boundary math — index

Every ECB/ECB-CBC trick lives or dies on alignment: where the service's fixed prefix ends and your controllable block boundary begins. Measure it before building any guess block.

## Related modules

- `block-alignment-deep.md` — mechanism internals and boundary conditions
- `block-alignment-checklist.md` — the ordered operational steps
- `block-alignment-catalogue.md` — case enumeration

## Cross-references

`ecb-detection.md` · `ecb-byte-at-a-time.md`
