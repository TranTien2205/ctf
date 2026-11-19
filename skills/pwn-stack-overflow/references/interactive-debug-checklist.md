# Interactive debugging without gdb — the r2 -d loop — checklist

gdb is absent; radare2 debugs: r2 -d runs the binary under a debugger — breakpoints, register reads, single-stepping through the crash.

## Checklist

- [ ] r2 -d ./chal — debug the binary.
- [ ] Set a breakpoint before the return: db <addr-of-ret>.
- [ ] Run (dc), send input at the read, hit the breakpoint.
- [ ] Read RSP/RBP and step over the ret — RIP's value is the proof.

## Abort conditions

- r2 -d is the only debugger here — no gdb.
- Remote services can't be r2 -d'd — measure from the remote fault instead.
- db <addr> then dc runs to the breakpoint.

## Falsifier

Falsifier — the binary can't be run under r2 -d (a remote service, a ptrace-blocked binary): use the remote fault or cyclic + service behavior instead.
