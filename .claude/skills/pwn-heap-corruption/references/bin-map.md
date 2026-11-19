# Which bin — the routing table


## Where a free lands

- size <= 0x410 (x64), tcache[i] not full → tcache.
- size <= fastbin max (~0x80), tcache full → fastbin.
- else → unsorted (one pass) → small/large on next alloc sweep.

## Where an alloc reads

- exact tcache match first, then fastbin (small sizes), then unsorted
  sweep, then small/large best-fit, then top.

## The lever

Drain tcache (7 per size) to force the bin you need; the routing table
is the control surface.
