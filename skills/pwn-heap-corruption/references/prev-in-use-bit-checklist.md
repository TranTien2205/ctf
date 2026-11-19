# The P bit — consolidation's switch — checklist

Companion to `prev-in-use-bit.md`.

## Checklist

- [ ] 1. Clear the next chunk's P (off-by-one into its size LSB).
- [ ] 2. Forge prev_size to point backward at your fake chunk.
- [ ] 3. free() merges backward into the fake → the merged chunk covers your
