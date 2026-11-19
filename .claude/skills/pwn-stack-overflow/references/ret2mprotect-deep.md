# ret2mprotect — make the stack executable — deep

Can't disable NX but can call mprotect: mark a region RWX, then write and jump to shellcode there.

## Mechanism internals

The chain is a layout, not a payload: each qword on the smashed stack is either a gadget address or a consumed argument, in order. The three invariants: (1) the offset to saved RIP is measured, not assumed — every build can shift it; (2) each gadget's consumed stack slots must be filled before the next address; (3) the chain ends only on an address that exists at runtime — PIE means base+offset.

## Boundary conditions

- The canary is the countermeasure: a leak or a write-around is required, else __stack_chk_fail.
- PIE + no leak means every address is unknown — a leak or a partial-overwrite trick is mandatory.
- Bad bytes in the read path (\x00 \x0a \x20 for most fgets/scanf) kill addresses containing them — pick different gadgets.
- movaps alignment inside libc faults on a misaligned stack — an extra ret gadget fixes parity.
- One-shot services can't re-trigger — the leak and the smash compose in one input, or the chain must be leak-free.

## Falsifier

Falsifier — mprotect not reachable (no PLT, no leak): can't make a region RWX — stick to ROP/syscall chains.

## Highest-cost traps

- mprotect(addr, len, PROT_READ|WRITE|EXEC=7).
- The buffer must be page-aligned for mprotect — use the page base.
- A simpler alternative under some stacks: call mmap for a fresh RWX region.

## Commands

```bash
readelf -s ./chal | grep -iE 'mprotect|mmap'
```

## Cross-references

`ret2shellcode.md` · `rop-basics.md`
