# Verifying the leaked value — the range check


A leaked value is a pointer — verify its range before arithmetic:

- 0x55/0x56xx — the binary (PIE) or an early heap.
- 0x7f.. — libc/mmap/ld.
- 0x7ff.. — the stack.
- small — an int, not a pointer.

A value in the wrong range means you read the wrong field.
