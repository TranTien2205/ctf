# Stack smash vs heap metadata — the ownership boundary — deep

Both are 'write past a buffer'; which class owns it depends on WHERE the corruption lands: stack frames belong here, heap chunk metadata belongs to pwn-heap-corruption.

## Mechanism internals

The chain is a layout: qword-by-qword, gadget addresses interleaved with their consumed stack slots, ending on an address that exists at runtime. Invariants: the offset is measured not assumed; each gadget's consumed slots are filled before the next address; PIE means every static address is base+offset.

## Boundary conditions

- Canary blocks a naive smash — leak or write around it.
- PIE + no leak means addresses are unknown.
- Bad bytes in the read path truncate addresses containing them.
- movaps alignment faults on a misaligned stack — ret-pad.
- One-shot services can't re-trigger — compose leak+smash in one input.

## Falsifier

Falsifier — the corruption demonstrably lands in heap metadata (a chunk header), not the stack frame: route to pwn-heap-corruption.

## Highest-cost traps

- Same primitive, different target — the cyclic test doesn't distinguish; the fault does.
- A malloc'd buffer can still be adjacent to stack-relevant data only in exotic layouts.
- The owning class decides which skill's chains apply.

## Commands

```bash
r2 -A ./chal && pdf @ <vuln>   # is the buffer local or malloc'd?
```

## Cross-references

`class-boundary.md` · `unsorted-bin-fd.md`
