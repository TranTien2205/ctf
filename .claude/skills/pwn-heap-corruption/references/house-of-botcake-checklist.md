# House of botcake — tcache/unsorted stacking — checklist

Companion to `house-of-botcake.md`.

## Checklist

- [ ] 1. Fill tcache count for size S (7 frees).
- [ ] 2. Free victim → unsorted bin (tcache full).
- [ ] 3. Corrupt victim's size/P-bit via overflow so consolidation covers a
- [ ] 4. Drain tcache; the consolidated chunk re-allocs over the neighbor —
