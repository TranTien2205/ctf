# Thread arenas — per-thread heap state — checklist

Companion to `thread-arena.md`.

## Checklist

- [ ] `N` flag bit marks non-main-arena chunks.
- [ ] A leak in a thread arena points at a different arena's base.
- [ ] Thread-spawned allocations have different addresses than main's.
- [ ] 1. Identify which thread issues the vulnerable alloc (main vs worker).
- [ ] 2. Non-main arena state lives in a separately-mmapped region — the
- [ ] 3. Corruption recipes still work, but offsets/leaks are per-arena.
