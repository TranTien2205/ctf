# Verifying the leaked value — the range check — checklist

Companion to `the-crosscheck-leak.md`.

## Checklist

- [ ] 0x55/0x56xx — the binary (PIE) or an early heap.
- [ ] 0x7f.. — libc/mmap/ld.
- [ ] 0x7ff.. — the stack.
- [ ] small — an int, not a pointer.
