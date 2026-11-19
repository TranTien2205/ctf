# Overflow spanning several chunks — checklist

Companion to `multi-chunk-overflow.md`.

## Checklist

- [ ] 1. Overflow past chunk A's data → B's header → C's header.
- [ ] 2. Forge B's size/flags AND C's — self-consistent fake chain.
- [ ] 3. A free/consolidate consumes the forged run — big overlap.
