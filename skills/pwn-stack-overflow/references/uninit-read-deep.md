# Uninitialized read as a leak primitive — deep

A buffer returned/read without full initialization carries stale stack bytes — pointers, the canary, addresses — a leak without a format string.

## Mechanism internals

The chain is a layout: qword-by-qword, gadget addresses interleaved with their consumed stack slots, ending on an address that exists at runtime. Invariants: the offset is measured not assumed; each gadget's consumed slots are filled before the next address; PIE means every static address is base+offset.

## Boundary conditions

- Canary blocks a naive smash — leak or write around it.
- PIE + no leak means addresses are unknown.
- Bad bytes in the read path truncate addresses containing them.
- movaps alignment faults on a misaligned stack — ret-pad.
- One-shot services can't re-trigger — compose leak+smash in one input.

## Falsifier

Falsifier — the buffer is fully written before being read: no stale bytes; no leak.

## Highest-cost traps

- The stale bytes vary per call — but the CANARY and return addresses are stable within a process.
- An uninit read is data-dependent — the offset to the canary varies; measure once.

## Cross-references

`canary-bypass.md` · `pie-leak.md`
