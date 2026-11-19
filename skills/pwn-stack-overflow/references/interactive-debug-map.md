# Interactive debugging without gdb — the r2 -d loop — map


## Signals

| Observation | Meaning | Route |
|---|---|---|
| need to see the crash register | r2 -d | breakpoint before ret |
| need to watch RIP at return | db the ret | step |
| need stack contents at smash | px @ rsp | read it |

## Falsifier

Falsifier — the binary can't be run under r2 -d (a remote service, a ptrace-blocked binary): use the remote fault or cyclic + service behavior instead.
