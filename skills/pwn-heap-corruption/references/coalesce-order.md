# Coalescing order — which neighbor merges first


Consolidation merges with the LOWER neighbor first (backward via
prev_size), then the upper. The order decides which live chunk gets
eaten.

## Steps

1. free() checks P bit of the NEXT chunk; if clear, walks prev_size
   back.
2. Then checks the higher neighbor (size + next's P).
3. Merged chunk goes to unsorted — a big hole covering live data.

## Exploitation

- To eat a HIGH neighbor: clear its P-bit only — the merge swallows it.
- To eat a LOW neighbor: forge the low chunk's prev_size/fd/bk
  (einherjar).

## Falsifier

The neighbor you need merged isn't marked free or the flags won't let
the walk reach it: the coalesce doesn't cover your target.
