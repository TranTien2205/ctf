# Return-address overwrite via %n — write into saved state — map


## Signals

| Observation | Meaning | Route |
|---|---|---|
| the saved return's stack address is known | the write target | %n to it |
| a leak gives the stack address | the target computable | %n there |
| want to redirect a return | ret addr overwrite | the chain |

## Falsifier

Falsifier — the saved return's stack address isn't predictable/leakable, or the write can't reach it: no ret-addr redirect.
