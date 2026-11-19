# Off-by-one and single-byte overwrites — deep

A single controlled byte past the buffer can still matter: zero the canary's low byte, shift the saved RBP's LSB, or corrupt a length field.

## Mechanism internals

The chain is a layout, not a payload: each qword on the smashed stack is either a gadget address or a consumed argument, in order. The three invariants: (1) the offset to saved RIP is measured, not assumed — every build can shift it; (2) each gadget's consumed stack slots must be filled before the next address; (3) the chain ends only on an address that exists at runtime — PIE means base+offset.

## Boundary conditions

- The canary is the countermeasure: a leak or a write-around is required, else __stack_chk_fail.
- PIE + no leak means every address is unknown — a leak or a partial-overwrite trick is mandatory.
- Bad bytes in the read path (\x00 \x0a \x20 for most fgets/scanf) kill addresses containing them — pick different gadgets.
- movaps alignment inside libc faults on a misaligned stack — an extra ret gadget fixes parity.
- One-shot services can't re-trigger — the leak and the smash compose in one input, or the chain must be leak-free.

## Falsifier

Falsifier — the overwritten byte reaches nothing security-relevant: no exploitable effect.

## Highest-cost traps

- The canary's low byte is always 0x00 — overwriting it with 0 keeps it valid.
- Saved-RBP LSB shifts the parent's frame — a pivot primitive.

## Cross-references

`saved-regs.md` · `canary-bypass.md`
