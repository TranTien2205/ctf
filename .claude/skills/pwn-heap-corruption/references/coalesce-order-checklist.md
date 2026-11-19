# Coalescing order — which neighbor merges first — checklist

Companion to `coalesce-order.md`.

## Checklist

- [ ] 1. free() checks P bit of the NEXT chunk; if clear, walks prev_size
- [ ] 2. Then checks the higher neighbor (size + next's P).
- [ ] 3. Merged chunk goes to unsorted — a big hole covering live data.
- [ ] To eat a HIGH neighbor: clear its P-bit only — the merge swallows it.
- [ ] To eat a LOW neighbor: forge the low chunk's prev_size/fd/bk
