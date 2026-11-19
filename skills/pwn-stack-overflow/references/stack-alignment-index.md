# Stack alignment — the movaps crash — index

x64 libc functions (especially system, printf) use movaps on the stack, which faults on misaligned RSP. A chain that crashes on the call site needs an extra 'ret' gadget for alignment.

## Related modules

- `stack-alignment-deep.md` — boundary conditions
- `stack-alignment-checklist.md` — operational steps
- `stack-alignment-catalogue.md` — case enumeration

## Cross-references

`ret2libc.md` · `troubleshoot.md`
