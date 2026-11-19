# Large-bin attack — the size-sorted write


The large bin is doubly-linked and size-sorted; corrupting a largebin
chunk's bk_nextsize writes a controlled pointer to a chosen address.

## The mechanism

Large-bin insert walks by size: `victim->bk_nextsize->fd_nextsize =
victim` — corrupt victim->bk_nextsize to point at target-0x20; the
insert writes &victim into target.

## Steps

1. Two large chunks: a victim in the large bin and one to insert.
2. Corrupt victim->bk_nextsize = target - 0x20 (x64).
3. Force an insertion that walks past the victim.
4. A pointer-sized value (the chunk address) lands at target.

## What it buys

A write of a heap address to a chosen slot — enough to corrupt
tcache_perthread_struct or a global counter.

## Falsifier

No large chunk is reachable or no insertion walks the victim: the
largebin route needs allocations large enough and the right bin path.
