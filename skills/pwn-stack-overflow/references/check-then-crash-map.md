# The crash that proves control — reading the fault correctly — map


## Signals

| Observation | Meaning | Route |
|---|---|---|
| RIP = pattern bytes | return control proven | the offset is right |
| fault address in write | a write crash, not return | the smash is writing |
| RIP = 0x41414141 | control proven | the smash reached RIP |
| RIP unchanged | didn't reach saved state | bound too short |

## Falsifier

Falsifier — RIP never holds controlled bytes at any tested length: no return-control exists at this bound.
