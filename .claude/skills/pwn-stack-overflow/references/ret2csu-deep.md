# ret2csu — the universal gadget pair — deep

__libc_csu_init carries two gadgets that set rdx, rsi, rdi, and call an arbitrary function — the fallback when the binary is sparse of clean pops.

## Mechanism internals

The chain is a layout, not a payload: each qword on the smashed stack is either a gadget address or a consumed argument, in order. The three invariants: (1) the offset to saved RIP is measured, not assumed — every build can shift it; (2) each gadget's consumed stack slots must be filled before the next address; (3) the chain ends only on an address that exists at runtime — PIE means base+offset.

## Boundary conditions

- The canary is the countermeasure: a leak or a write-around is required, else __stack_chk_fail.
- PIE + no leak means every address is unknown — a leak or a partial-overwrite trick is mandatory.
- Bad bytes in the read path (\x00 \x0a \x20 for most fgets/scanf) kill addresses containing them — pick different gadgets.
- movaps alignment inside libc faults on a misaligned stack — an extra ret gadget fixes parity.
- One-shot services can't re-trigger — the leak and the smash compose in one input, or the chain must be leak-free.

## Falsifier

Falsifier — statically linked or stripped binary without __libc_csu_init: the universal pair doesn't exist.

## Highest-cost traps

- r12 must hold the ADDRESS of a pointer to the function (a GOT slot), not the function itself.
- The body gadget's 'call' jumps to [r12+rbx*8] — an indirect call, not a ret-based transfer.
- r13d is edi (32-bit!) — zero the upper half if the arg needs 64 bits.

## Commands

```bash
readelf -s ./chal | grep csu
r2 -A ./chal && pdf @ __libc_csu_init
```

## Cross-references

`rop-basics.md` · `ret2libc.md`
