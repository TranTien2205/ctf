# The empirical chain — build small, test each


Build the chain incrementally: one gadget, verify; then the next —
never write the whole chain blind.

## The loop

1. pop rdi ; marker — verify rdi lands right (r2 -d, dr rdi).
2. Add the next gadget — verify again.
3. The call — verify the target reached (the crash or the behavior).

## The tool

r2 -d ./chal with a breakpoint at the overwrite point — step the chain
gadget by gadget.

## Falsifier

A gadget mid-chain doesn't behave as expected: isolate and re-scan.
