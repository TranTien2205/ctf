# Stack pivot — when the writable area is too small — deep

The buffer is too small for the chain, or the stack isn't where you want it. Pivot: point RSP elsewhere with a 'leave; ret' or 'xchg rsp, rXx' gadget.

## Mechanism internals

The chain is a layout, not a payload: each qword on the smashed stack is either a gadget address or a consumed argument, in order. The three invariants: (1) the offset to saved RIP is measured, not assumed — every build can shift it; (2) each gadget's consumed stack slots must be filled before the next address; (3) the chain ends only on an address that exists at runtime — PIE means base+offset.

## Boundary conditions

- The canary is the countermeasure: a leak or a write-around is required, else __stack_chk_fail.
- PIE + no leak means every address is unknown — a leak or a partial-overwrite trick is mandatory.
- Bad bytes in the read path (\x00 \x0a \x20 for most fgets/scanf) kill addresses containing them — pick different gadgets.
- movaps alignment inside libc faults on a misaligned stack — an extra ret gadget fixes parity.
- One-shot services can't re-trigger — the leak and the smash compose in one input, or the chain must be leak-free.

## Falsifier

Falsifier — no controllable RBP and no xchg/add-rsp gadget: no pivot exists.

## Highest-cost traps

- 'leave; ret' uses RBP — you need RBP control, usually from the same smash.
- The staged buffer must be readable/writable and known-address — a bss or heap region.
- Two-stage attacks need two writes or one write to the staged area.

## Commands

```bash
r2 -A ./chal && /R leave
```

## Cross-references

`rop-basics.md` · `fgot-overwrite.md`
