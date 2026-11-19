# Pointer arithmetic in the leak — naming each dump value


Each %p value is a guess until named: binary-range, libc-range,
stack-range, heap-range — classify by the high bits.

## Ranges (typical x64, PIE)

- 0x55xxxxxxxxxx / 0x56xxxxxxxxxx — the binary (PIE base).
- 0x7fxxxxxxxxxx — libc / mmap / ld.
- 0x7ffxxxxxxxxxx — the stack.
- 0x0000555x.. vs 0x00007ffx.. — the leading zeroes differ.

## Naming each

- A code pointer near a known function: binary base.
- A pointer near a known import: libc.
- A pointer near argv/env: stack top.
- Small values: ints, sizes, counters — not pointers.
