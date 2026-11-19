# free() checks — the gates on deallocation — checklist

Companion to `the-free-checks.md`.

## Checklist

- [ ] 1. Pointer alignment — chunk boundary (0x10 x64).
- [ ] 2. Size sanity — >= MINSIZE, sane upper bound.
- [ ] 3. Next-size sanity — the following chunk's size must be valid.
- [ ] 4. tcache key check (2.29+) — the double-free detector.
- [ ] 5. fastbin top check — top != victim.
- [ ] 6. Consolidation window — the merge's own checks.
