# One-shot constraints — no re-trigger — deep

The service runs once: no leak-then-exploit. The whole attack must fit a single input — or the leak must be embedded.

## Mechanism internals

The chain is a layout, not a payload: each qword on the smashed stack is either a gadget address or a consumed argument, in order. The three invariants: (1) the offset to saved RIP is measured, not assumed — every build can shift it; (2) each gadget's consumed stack slots must be filled before the next address; (3) the chain ends only on an address that exists at runtime — PIE means base+offset.

## Boundary conditions

- The canary is the countermeasure: a leak or a write-around is required, else __stack_chk_fail.
- PIE + no leak means every address is unknown — a leak or a partial-overwrite trick is mandatory.
- Bad bytes in the read path (\x00 \x0a \x20 for most fgets/scanf) kill addresses containing them — pick different gadgets.
- movaps alignment inside libc faults on a misaligned stack — an extra ret gadget fixes parity.
- One-shot services can't re-trigger — the leak and the smash compose in one input, or the chain must be leak-free.

## Falsifier

Falsifier — the chain genuinely needs two stages and the service is one-shot: find a leak-free alternative or a different bug.

## Highest-cost traps

- A leak-free chain exists when ASLR leaves some bytes predictable, or when the target is non-PIE + no-leak-needed.
- The same-input composition: leak via a format read inside the smash, then use it.
- The least-squares answer: brute-force the one unknown byte across many runs.

## Cross-references

`second-stage.md` · `remote-vs-local.md`
