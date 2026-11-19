# The crash that proves control — reading the fault correctly — deep

A segfault is only evidence when the faulting register holds your bytes. Read the fault correctly: RIP for control, a data register for a write crash.

## Mechanism internals

The chain is a layout: qword-by-qword, gadget addresses interleaved with their consumed stack slots, ending on an address that exists at runtime. Invariants: the offset is measured not assumed; each gadget's consumed slots are filled before the next address; PIE means every static address is base+offset.

## Boundary conditions

- Canary blocks a naive smash — leak or write around it.
- PIE + no leak means addresses are unknown.
- Bad bytes in the read path truncate addresses containing them.
- movaps alignment faults on a misaligned stack — ret-pad.
- One-shot services can't re-trigger — compose leak+smash in one input.

## Falsifier

Falsifier — RIP never holds controlled bytes at any tested length: no return-control exists at this bound.

## Highest-cost traps

- The 'crash' is the signal; the register tells you WHICH crash.
- A SIGSEGV at a write into your input is a write-crash, not a return-crash.
- Remote: the service may not expose the register — infer from the disconnect behavior.

## Commands

```bash
r2 -d ./chal
python3 tools/pwn_cyclic.py --find <bytes>
```

## Cross-references

`offset-measurement.md` · `cyclic-offset.md`
