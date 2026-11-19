# Function-pointer overwrite — the indirect-call target — map


## Signals

| Observation | Meaning | Route |
|---|---|---|
| a function pointer in the smashed region | call-control | overwrite it |
| a callback invoked after the write | the call happens | redirect it |
| atexit or a handler table on stack | exit-time call | overwrite the entry |

## Falsifier

Falsifier — no function pointer reachable by the write, or none is called after the write point: no call-control.
