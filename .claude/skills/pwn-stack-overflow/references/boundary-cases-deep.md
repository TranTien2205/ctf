# Boundary cases — where the textbook breaks — deep

Each entry: the boundary, why the recipe breaks, the fix.

## Mechanism internals

The chain is a layout, not a payload: each qword on the smashed stack is either a gadget address or a consumed argument, in order. The three invariants: (1) the offset to saved RIP is measured, not assumed — every build can shift it; (2) each gadget's consumed stack slots must be filled before the next address; (3) the chain ends only on an address that exists at runtime — PIE means base+offset.

## Boundary conditions

- The canary is the countermeasure: a leak or a write-around is required, else __stack_chk_fail.
- PIE + no leak means every address is unknown — a leak or a partial-overwrite trick is mandatory.
- Bad bytes in the read path (\x00 \x0a \x20 for most fgets/scanf) kill addresses containing them — pick different gadgets.
- movaps alignment inside libc faults on a misaligned stack — an extra ret gadget fixes parity.
- One-shot services can't re-trigger — the leak and the smash compose in one input, or the chain must be leak-free.

## Falsifier

Falsifier — the offset math from the textbook fails because the build flags differ: always measure offsets empirically.

## Highest-cost traps

- x86 (32-bit) chains put args on the stack — simpler ROP layout.
- Static binaries carry no libc — only syscalls, no system@plt.
- -fomit-frame-pointer removes saved RBP — the leave;ret pivot dies.

## Commands

```bash
readelf -h ./chal | grep -iE 'class|type'
```

## Cross-references

`saved-regs.md` · `stack-alignment.md`
