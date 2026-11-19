# The crash that proves control — reading the fault correctly — case catalogue

A segfault is only evidence when the faulting register holds your bytes. Read the fault correctly: RIP for control, a data register for a write crash.

## Cases

| # | Shape | Meaning | Route |
|---|---|---|---|
| 1 | RIP = pattern bytes | return control proven | the offset is right |
| 2 | fault address in write | a write crash, not return | the smash is writing |
| 3 | RIP = 0x41414141 | control proven | the smash reached RIP |
| 4 | RIP unchanged | didn't reach saved state | bound too short |

## Falsifier

Falsifier — RIP never holds controlled bytes at any tested length: no return-control exists at this bound.
