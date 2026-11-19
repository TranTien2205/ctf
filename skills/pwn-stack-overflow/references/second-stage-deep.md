# Two-stage exploits — leak first, then exploit — deep

Many chains need two rounds: first a leak (canary, libc base, stack address), then the real payload built with the leaked values.

## Mechanism internals

The chain is a layout, not a payload: each qword on the smashed stack is either a gadget address or a consumed argument, in order. The three invariants: (1) the offset to saved RIP is measured, not assumed — every build can shift it; (2) each gadget's consumed stack slots must be filled before the next address; (3) the chain ends only on an address that exists at runtime — PIE means base+offset.

## Boundary conditions

- The canary is the countermeasure: a leak or a write-around is required, else __stack_chk_fail.
- PIE + no leak means every address is unknown — a leak or a partial-overwrite trick is mandatory.
- Bad bytes in the read path (\x00 \x0a \x20 for most fgets/scanf) kill addresses containing them — pick different gadgets.
- movaps alignment inside libc faults on a misaligned stack — an extra ret gadget fixes parity.
- One-shot services can't re-trigger — the leak and the smash compose in one input, or the chain must be leak-free.

## Falsifier

Falsifier — the service doesn't re-trigger and the chain needs two stages: single-shot is required — combine the leak and the smash in one input if the protocol allows.

## Highest-cost traps

- Fork-per-connection gives clean re-trigger; single-process doesn't.
- Same-connection re-trigger needs the service to loop back to the read.
- A canary/base leaked in stage 1 is valid only for that process.

## Cross-references

`canary-bypass.md` · `ret2libc.md`
