# Always unsorted-leak first — the cheapest stage — checklist

Companion to `the-unsorted-first.md`.

## Checklist

- [ ] 1. Drain tcache for size S>0x80 (7 frees).
- [ ] 2. Free victim → unsorted; fd/bk = &main_arena.bins[..].
- [ ] 3. Dangling read → the libc address.
- [ ] 4. base = leaked - offset (from the shipped libc).
