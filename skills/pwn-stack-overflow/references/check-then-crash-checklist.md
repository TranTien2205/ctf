# The crash that proves control — reading the fault correctly — checklist

A segfault is only evidence when the faulting register holds your bytes. Read the fault correctly: RIP for control, a data register for a write crash.

## Checklist

- [ ] Run under r2 -d or read the kernel's core/dmesg for the faulting register.
- [ ] RIP = pattern bytes → the return was hijacked → measure offset.
- [ ] Fault in the write path (mov to your controlled ptr) → a different primitive.
- [ ] No RIP control → the write didn't reach saved state.

## Abort conditions

- The 'crash' is the signal; the register tells you WHICH crash.
- A SIGSEGV at a write into your input is a write-crash, not a return-crash.
- Remote: the service may not expose the register — infer from the disconnect behavior.

## Falsifier

Falsifier — RIP never holds controlled bytes at any tested length: no return-control exists at this bound.
