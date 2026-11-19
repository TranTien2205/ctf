# PIE leak — getting the code base under ASLR — index

PIE randomizes the binary's base: every function/gadget/data address is base+offset. A leak of ANY code/data pointer gives the base.

## Related modules

- `pie-leak-deep.md` — boundary conditions
- `pie-leak-checklist.md` — operational steps
- `pie-leak-catalogue.md` — case enumeration

## Cross-references

`protection-modes.md` · `canary-bypass.md`
