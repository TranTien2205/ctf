# More write targets — the stack data itself — checklist

Companion to `alternate-write-targets2.md`.

## Checklist

- [ ] A bounds var on the stack → patch the bound.
- [ ] A loop counter/flag on stack → patch control flow.
- [ ] A vtable pointer → virtual-call redirect.
- [ ] 1. Stack locals are at leakable addresses — %n to a length/index/bounds
- [ ] 2. A patched bound lets a later bounded-read overflow.
- [ ] 3. A patched flag/enum flips a check.
