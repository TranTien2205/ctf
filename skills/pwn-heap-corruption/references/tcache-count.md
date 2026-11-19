# tcache counts[] — the per-size tally


tcache_perthread_struct holds counts[64] — glibc checks the count
before returning a tcache chunk. Corrupting a count fabricates free
chunks.

## Steps

1. tcache struct sits at the heap's start (usually heap_base+0x10).
2. Write count[i] = N for a size i — the bin now believes it holds N
   chunks.
3. The next alloc of size i follows the (corrupted or stale) entry
   chain — or returns garbage from a null chain.

## Notes

- counts[] is a byte array — a single byte-write suffices.
- Combined with entry corruption, it's arbitrary allocs.

## Falsifier

The struct isn't writable by the bug's reach: counts are safe — the
entries themselves must be the target.
