# ret2dlresolve — resolving a symbol that was never imported — deep

The dynamic linker's lazy-resolution machinery can be tricked into resolving an ARBITRARY symbol name at runtime: craft fake relocation/symbol/string entries, call the resolver stub, and 'system' materializes even though the binary never imported it.

## Mechanism internals

The chain is a layout: qword-by-qword, gadget addresses interleaved with their consumed stack slots, ending on an address that exists at runtime. Invariants: the offset is measured not assumed; each gadget's consumed slots are filled before the next address; PIE means every static address is base+offset.

## Boundary conditions

- Canary blocks a naive smash — leak or write around it.
- PIE + no leak means addresses are unknown.
- Bad bytes in the read path truncate addresses containing them.
- movaps alignment faults on a misaligned stack — ret-pad.
- One-shot services can't re-trigger — compose leak+smash in one input.

## Falsifier

Falsifier — no writable place for the fake structures, or the resolver stub isn't reachable: ret2dlresolve can't run.

## Highest-cost traps

- Full RELRO binds everything at startup — the lazy-resolve path is closed.
- The fake structures must be at a known, readable address — a bss region usually.
- x64 uses JMPREL entries; the index math differs from x86.

## Commands

```bash
readelf -r ./chal
readelf -S ./chal | grep -iE 'plt|got|rela'
```

## Cross-references

`ret2libc.md` · `fgot-overwrite.md`
