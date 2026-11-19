# Overlapping chunks — the goal of most grooming — checklist

Companion to `overlapping-chunks.md`.

## Checklist

- [ ] Double-free: one chunk allocated twice.
- [ ] Off-by-one + consolidate: live chunk eaten by a bigger free chunk.
- [ ] Size corruption: a chunk enlarged to cover its neighbor.
- [ ] Tcache/fastbin dup: same slot returned twice.
- [ ] A "data" object overlapping a "pointer" object → forge a pointer →
- [ ] A chunk overlapping a freed chunk → control fd/bk directly.
