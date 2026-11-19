# Function-pointer overwrite — the indirect-call target — deep

A function pointer stored on the stack (a callback, a handler table, an atexit entry) that's overwritten becomes a controlled call site — call instead of return.

## Mechanism internals

The chain is a layout: qword-by-qword, gadget addresses interleaved with their consumed stack slots, ending on an address that exists at runtime. Invariants: the offset is measured not assumed; each gadget's consumed slots are filled before the next address; PIE means every static address is base+offset.

## Boundary conditions

- Canary blocks a naive smash — leak or write around it.
- PIE + no leak means addresses are unknown.
- Bad bytes in the read path truncate addresses containing them.
- movaps alignment faults on a misaligned stack — ret-pad.
- One-shot services can't re-trigger — compose leak+smash in one input.

## Falsifier

Falsifier — no function pointer reachable by the write, or none is called after the write point: no call-control.

## Highest-cost traps

- The call's arguments come from the call site, not your payload — check what rdi holds.
- A vtable pointer overwrite is the C++ version of this.
- atexit hooks run on clean exit — a clean exit path can trigger your call.

## Commands

```bash
r2 -A ./chal && pdf @ <func> | grep -iE 'call|icall'
```

## Cross-references

`control-flow.md` · `write-where.md`
