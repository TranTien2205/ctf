# When every stack route is closed — the handoff — deep

Full RELRO + canary + PIE + NX + no leak primitive: every stack-corruption route is falsified. The honest move is to record the dead routes and hand back to the router.

## Mechanism internals

The chain is a layout: qword-by-qword, gadget addresses interleaved with their consumed stack slots, ending on an address that exists at runtime. Invariants: the offset is measured not assumed; each gadget's consumed slots are filled before the next address; PIE means every static address is base+offset.

## Boundary conditions

- Canary blocks a naive smash — leak or write around it.
- PIE + no leak means addresses are unknown.
- Bad bytes in the read path truncate addresses containing them.
- movaps alignment faults on a misaligned stack — ret-pad.
- One-shot services can't re-trigger — compose leak+smash in one input.

## Falsifier

Falsifier — a falsifier that doesn't hold (e.g., 'full RELRO' was actually partial): recheck the protection evidence.

## Highest-cost traps

- The honest output is the falsifier that closes each route — not 'it didn't work'.
- A closed stack route can coexist with an open heap/format/logic route.
- The kill map in knowledge/attempts/ records this for the next attempt.

## Cross-references

`negative-results.md` · `class-boundary.md`
