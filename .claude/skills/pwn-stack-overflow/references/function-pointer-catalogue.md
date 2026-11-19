# Function-pointer overwrite — the indirect-call target — case catalogue

A function pointer stored on the stack (a callback, a handler table, an atexit entry) that's overwritten becomes a controlled call site — call instead of return.

## Cases

| # | Shape | Meaning | Route |
|---|---|---|---|
| 1 | a function pointer in the smashed region | call-control | overwrite it |
| 2 | a callback invoked after the write | the call happens | redirect it |
| 3 | atexit or a handler table on stack | exit-time call | overwrite the entry |

## Falsifier

Falsifier — no function pointer reachable by the write, or none is called after the write point: no call-control.
