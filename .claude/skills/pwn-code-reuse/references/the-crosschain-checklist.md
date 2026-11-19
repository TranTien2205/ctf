# Cross-checking the chain — the pre-fire audit — checklist

Companion to `the-crosschain.md`.

## Checklist

- [ ] 1. Every gadget's address is real (r2 /R verified).
- [ ] 2. Every arg's value is correct (computed against the real base).
- [ ] 3. The alignment is right (the movaps check).
- [ ] 4. The call's args are set by the preceding pops.
- [ ] 5. The ending lands somewhere observable.
