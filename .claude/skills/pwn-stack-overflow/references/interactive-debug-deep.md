# Interactive debugging without gdb — the r2 -d loop — deep

gdb is absent; radare2 debugs: r2 -d runs the binary under a debugger — breakpoints, register reads, single-stepping through the crash.

## Mechanism internals

The chain is a layout: qword-by-qword, gadget addresses interleaved with their consumed stack slots, ending on an address that exists at runtime. Invariants: the offset is measured not assumed; each gadget's consumed slots are filled before the next address; PIE means every static address is base+offset.

## Boundary conditions

- Canary blocks a naive smash — leak or write around it.
- PIE + no leak means addresses are unknown.
- Bad bytes in the read path truncate addresses containing them.
- movaps alignment faults on a misaligned stack — ret-pad.
- One-shot services can't re-trigger — compose leak+smash in one input.

## Falsifier

Falsifier — the binary can't be run under r2 -d (a remote service, a ptrace-blocked binary): use the remote fault or cyclic + service behavior instead.

## Highest-cost traps

- r2 -d is the only debugger here — no gdb.
- Remote services can't be r2 -d'd — measure from the remote fault instead.
- db <addr> then dc runs to the breakpoint.

## Commands

```bash
r2 -d ./chal
r2 -d ./chal -c 'db main+offset; dc; px @ rsp'
```

## Cross-references

`tools-radare2.md` · `offset-measurement.md`
