# Endianness and register width — x86 vs x64 — index

x86 (32-bit) args go on the stack; x64 args go in rdi/rsi/rdx. Pattern chunks and addresses are 4 vs 8 bytes. Get the width right or the chain is garbage.

## Related modules

- `endianness-and-width-deep.md` — boundary conditions
- `endianness-and-width-checklist.md` — operational steps
- `endianness-and-width-catalogue.md` — case enumeration

## Cross-references

`boundary-cases.md` · `rop-basics.md`
