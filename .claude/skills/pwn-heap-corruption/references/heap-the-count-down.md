# counts[i]-- — the alloc-side check


On alloc, counts[i] is decremented — a poisoned count of 0 makes the
bin look empty (the alloc skips it entirely even with a live entry).

## The consequence

- A stale count of 0 with a valid entry: the entry is unreachable.
- A count set higher than real entries: the walk runs past the tail —
  crash or wild return.

## Falsifier

The count can't be set to what you need: the entry chain must match.
