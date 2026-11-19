# The stack leak — for ret-addr targets — checklist

Companion to `the-stack-leak.md`.

## Checklist

- [ ] A saved rbp in the dump — *rbp+8 = saved ret.
- [ ] environ — libc global → stack pointer.
- [ ] An argv pointer — the stack top.
