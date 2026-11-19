# Write alignment — the pointer must be arg-aligned — checklist

Companion to `the-write-alignment.md`.

## Checklist

- [ ] 1. x64 args are 8-byte slots — the pointer must fill one.
- [ ] 2. If your input bytes place it off-boundary, the deref reads the wrong
- [ ] 3. Pad the input so the address lands on an 8-byte boundary.
- [ ] 4. Check alignment with %N$p — it should print YOUR address exactly.
