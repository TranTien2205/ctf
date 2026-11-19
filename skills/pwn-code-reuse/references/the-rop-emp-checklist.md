# The empirical chain — build small, test each — checklist

Companion to `the-rop-emp.md`.

## Checklist

- [ ] 1. pop rdi ; marker — verify rdi lands right (r2 -d, dr rdi).
- [ ] 2. Add the next gadget — verify again.
- [ ] 3. The call — verify the target reached (the crash or the behavior).
