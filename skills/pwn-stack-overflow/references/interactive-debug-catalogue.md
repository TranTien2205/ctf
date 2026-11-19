# Interactive debugging without gdb — the r2 -d loop — case catalogue

gdb is absent; radare2 debugs: r2 -d runs the binary under a debugger — breakpoints, register reads, single-stepping through the crash.

## Cases

| # | Shape | Meaning | Route |
|---|---|---|---|
| 1 | need to see the crash register | r2 -d | breakpoint before ret |
| 2 | need to watch RIP at return | db the ret | step |
| 3 | need stack contents at smash | px @ rsp | read it |

## Falsifier

Falsifier — the binary can't be run under r2 -d (a remote service, a ptrace-blocked binary): use the remote fault or cyclic + service behavior instead.
