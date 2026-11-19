# House of botcake — tcache/unsorted stacking


Stack tcache and unsorted-bin state so one free lands a chunk in BOTH
bins: free → tcache dup → still in unsorted → overlapping chunks on
modern glibc (2.32+ compatible with safe-linking if you leak first).

## Shape

1. Fill tcache count for size S (7 frees).
2. Free victim → unsorted bin (tcache full).
3. Corrupt victim's size/P-bit via overflow so consolidation covers a
   neighbor.
4. Drain tcache; the consolidated chunk re-allocs over the neighbor —
   overlap.

## Falsifier

Consolidation can't reach the victim (no clearable P-bit or no
controllable neighbor): botcake's overlap never forms.
