# Zeroing registers — xor/mov substitutes — checklist

Companion to `the-xor-zero.md`.

## Checklist

- [ ] xor reg,reg clears the whole register — good for NULL args.
- [ ] On x86-64, writing the 32-bit register zeroes the top — xor edx,edx
