# Function-pointer overwrite — the indirect-call target

A function pointer stored on the stack (a callback, a handler table, an atexit entry) that's overwritten becomes a controlled call site — call instead of return.

## Signals

| Observation | Meaning | Route |
|---|---|---|
| a function pointer in the smashed region | call-control | overwrite it |
| a callback invoked after the write | the call happens | redirect it |
| atexit or a handler table on stack | exit-time call | overwrite the entry |

## Steps

1. Find a function pointer the code calls AFTER your write point.
2. Overwrite the pointer with the target address.
3. The next indirect call goes to your target — system() if the arg registers are right.
4. The arg to the call is whatever the calling code set — check what it passes.

## Falsifier

Falsifier — no function pointer reachable by the write, or none is called after the write point: no call-control.

## Traps

- The call's arguments come from the call site, not your payload — check what rdi holds.
- A vtable pointer overwrite is the C++ version of this.
- atexit hooks run on clean exit — a clean exit path can trigger your call.

## Commands

```bash
r2 -A ./chal && pdf @ <func> | grep -iE 'call|icall'
```

## Cross-references

`control-flow.md` · `write-where.md`
