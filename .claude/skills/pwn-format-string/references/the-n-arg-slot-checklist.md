# The %N$n arg slot — must hold a POINTER — checklist

Companion to `the-n-arg-slot.md`.

## Checklist

- [ ] 1. The arg slot must contain the target's ADDRESS, 8-byte aligned on x64.
- [ ] 2. If your input's bytes form the pointer, align them to the boundary.
- [ ] 3. A 4-byte-misaligned pointer writes to the wrong address.
