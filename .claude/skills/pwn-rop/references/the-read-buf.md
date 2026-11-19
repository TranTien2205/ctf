# The read buffer — choosing the stage-2 home


Where stage 2 lands: a writable region at a known address —

- .bss: fixed under non-PIE.
- The heap: needs a heap leak.
- The stack: needs a stack leak.

## The choice

.bss under non-PIE is the standard; under PIE, the code leak gives
the section's address.
