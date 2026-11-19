# Fastbin dup — the A-B-A double free — checklist

Companion to `fastbin-dup.md`.

## Checklist

- [ ] 1. Three small chunks (<= 0x80): A, B, guard.
- [ ] 2. free A → fastbin top = A.
- [ ] 3. free B → top = B (A still linked).
- [ ] 4. free A again → top = A, A's fd points to B — the bin is corrupted.
- [ ] 5. Next mallocs return A, B, then A AGAIN → overlapping chunks.
- [ ] 6. Overwrite A's fd to a target → dup-into-target.
- [ ] Sizes must fit the fastbin range.
- [ ] tcache intercepts frees first on 2.26+ — exhaust the tcache size bin
