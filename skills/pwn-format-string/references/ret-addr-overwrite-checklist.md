# Return-address overwrite via %n — write into saved state — checklist

The saved return address on the stack is a write target: overwrite it with the target's address and the function's return goes to your chain — %n as the write primitive.

## Checklist

- [ ] Leak or compute the saved return address's stack location.
- [ ] Plant that stack address as a %N$n arg; write the target address into it.
- [ ] The function's return reads the overwritten address — execution redirects.
- [ ] Chain: %n writes the ret-addr; the return lands on a gadget/function.

## Abort conditions

- The saved return's address is a STACK address — needs a stack leak or predictable layout.
- %n writes 8 bytes — usually you want %hhn at controlled offsets for a targeted value.
- PIE + ASLR means the stack address must be leaked.

## Falsifier

Falsifier — the saved return's stack address isn't predictable/leakable, or the write can't reach it: no ret-addr redirect.
