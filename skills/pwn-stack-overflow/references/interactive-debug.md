# Interactive debugging without gdb — the r2 -d loop

gdb is absent; radare2 debugs: r2 -d runs the binary under a debugger — breakpoints, register reads, single-stepping through the crash.

## Signals

| Observation | Meaning | Route |
|---|---|---|
| need to see the crash register | r2 -d | breakpoint before ret |
| need to watch RIP at return | db the ret | step |
| need stack contents at smash | px @ rsp | read it |

## Steps

1. r2 -d ./chal — debug the binary.
2. Set a breakpoint before the return: db <addr-of-ret>.
3. Run (dc), send input at the read, hit the breakpoint.
4. Read RSP/RBP and step over the ret — RIP's value is the proof.

## Falsifier

Falsifier — the binary can't be run under r2 -d (a remote service, a ptrace-blocked binary): use the remote fault or cyclic + service behavior instead.

## Traps

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
