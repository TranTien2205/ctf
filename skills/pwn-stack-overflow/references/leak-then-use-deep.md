# Leak-then-use — composing the two primitives — deep

The standard hard-case chain: an info-leak primitive (format-string, uninit read) feeds values into the stack-smash payload — leak first, exploit second.

## Mechanism internals

The chain is a layout: qword-by-qword, gadget addresses interleaved with their consumed stack slots, ending on an address that exists at runtime. Invariants: the offset is measured not assumed; each gadget's consumed slots are filled before the next address; PIE means every static address is base+offset.

## Boundary conditions

- Canary blocks a naive smash — leak or write around it.
- PIE + no leak means addresses are unknown.
- Bad bytes in the read path truncate addresses containing them.
- movaps alignment faults on a misaligned stack — ret-pad.
- One-shot services can't re-trigger — compose leak+smash in one input.

## Falsifier

Falsifier — the service can't re-trigger and the primitives can't compose in one input: the two-stage is impossible; need a leak-free chain.

## Highest-cost traps

- The leaked value is valid only for that process instance.
- Fork-per-connection: same canary; exec-per-connection: re-leak each time.
- Compose in one input if the protocol allows a format read inside the smash.

## Cross-references

`second-stage.md` · `one-shot-constraints.md`
