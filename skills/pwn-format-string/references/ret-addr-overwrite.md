# Return-address overwrite via %n — write into saved state

The saved return address on the stack is a write target: overwrite it with the target's address and the function's return goes to your chain — %n as the write primitive.

## Signals

| Observation | Meaning | Route |
|---|---|---|
| the saved return's stack address is known | the write target | %n to it |
| a leak gives the stack address | the target computable | %n there |
| want to redirect a return | ret addr overwrite | the chain |

## Steps

1. Leak or compute the saved return address's stack location.
2. Plant that stack address as a %N$n arg; write the target address into it.
3. The function's return reads the overwritten address — execution redirects.
4. Chain: %n writes the ret-addr; the return lands on a gadget/function.

## Falsifier

Falsifier — the saved return's stack address isn't predictable/leakable, or the write can't reach it: no ret-addr redirect.

## Traps

- The saved return's address is a STACK address — needs a stack leak or predictable layout.
- %n writes 8 bytes — usually you want %hhn at controlled offsets for a targeted value.
- PIE + ASLR means the stack address must be leaked.

## Cross-references

`got-overwrite-fmt.md` · `arb-write-via-n.md`
