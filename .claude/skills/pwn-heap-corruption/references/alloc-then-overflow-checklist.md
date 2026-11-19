# Alloc-then-overflow — the boundary write — checklist

Companion to `alloc-then-overflow.md`.

## Checklist

- [ ] 1. alloc A(size) — alloc B(size) — adjacency.
- [ ] 2. A's write op overruns into B's size field.
- [ ] 3. Forge B's size/flags → the techniques open (off-by-one family,
