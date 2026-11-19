# Nested frames — the overflow inside a called function — deep

The vulnerable read often sits inside a helper function called by main: the smash controls the HELPER's return first, then main's — a chain across frames.

## Mechanism internals

The chain is a layout: qword-by-qword, gadget addresses interleaved with their consumed stack slots, ending on an address that exists at runtime. Invariants: the offset is measured not assumed; each gadget's consumed slots are filled before the next address; PIE means every static address is base+offset.

## Boundary conditions

- Canary blocks a naive smash — leak or write around it.
- PIE + no leak means addresses are unknown.
- Bad bytes in the read path truncate addresses containing them.
- movaps alignment faults on a misaligned stack — ret-pad.
- One-shot services can't re-trigger — compose leak+smash in one input.

## Falsifier

Falsifier — only the helper's return is reachable and the useful redirect needs main's frame: the second return is unreachable.

## Highest-cost traps

- Each frame's return is independently overwritable in one smash.
- The helper's return goes first; plan the sequence.

## Commands

```bash
r2 -A ./chal && pdf @ <helper>
```

## Cross-references

`saved-regs.md` · `offset-measurement.md`
