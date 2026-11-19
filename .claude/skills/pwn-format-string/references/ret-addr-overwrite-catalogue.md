# Return-address overwrite via %n — write into saved state — case catalogue

The saved return address on the stack is a write target: overwrite it with the target's address and the function's return goes to your chain — %n as the write primitive.

## Cases

| # | Shape | Meaning | Route |
|---|---|---|---|
| 1 | the saved return's stack address is known | the write target | %n to it |
| 2 | a leak gives the stack address | the target computable | %n there |
| 3 | want to redirect a return | ret addr overwrite | the chain |

## Falsifier

Falsifier — the saved return's stack address isn't predictable/leakable, or the write can't reach it: no ret-addr redirect.
