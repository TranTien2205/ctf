# Flag-in-memory — reading it off the heap — checklist

Companion to `the-flag-in-mem.md`.

## Checklist

- [ ] 1. Leak the flag object's address (a pointer array, a known layout).
- [ ] 2. Arbitrary read via overlap/type-confusion → the flag bytes.
- [ ] 3. The flag is in the read output — feed the hook.
