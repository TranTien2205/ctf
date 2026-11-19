# Saved registers — the frame layout — deep

The stack frame: [locals][canary?][saved RBP][saved RIP][args]. Smashing past saved RBP hits saved RIP — the offset math lives here.

## Mechanism internals

The chain is a layout, not a payload: each qword on the smashed stack is either a gadget address or a consumed argument, in order. The three invariants: (1) the offset to saved RIP is measured, not assumed — every build can shift it; (2) each gadget's consumed stack slots must be filled before the next address; (3) the chain ends only on an address that exists at runtime — PIE means base+offset.

## Boundary conditions

- The canary is the countermeasure: a leak or a write-around is required, else __stack_chk_fail.
- PIE + no leak means every address is unknown — a leak or a partial-overwrite trick is mandatory.
- Bad bytes in the read path (\x00 \x0a \x20 for most fgets/scanf) kill addresses containing them — pick different gadgets.
- movaps alignment inside libc faults on a misaligned stack — an extra ret gadget fixes parity.
- One-shot services can't re-trigger — the leak and the smash compose in one input, or the chain must be leak-free.

## Falsifier

Falsifier — the write stops before the saved registers: the bound is too short; check the read's bound.

## Highest-cost traps

- The canary (if any) sits between locals and saved regs — corrupting it trips __stack_chk_fail.
- Frame layout varies with optimization — measure, don't assume the textbook layout.

## Commands

```bash
r2 -A ./chal && pdf @ <func>
```

## Cross-references

`offset-measurement.md` · `canary-bypass.md`
