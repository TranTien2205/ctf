# The sorted bins — small/large ordering


Small and large bins are sorted (by size for large, FIFO-ish for
small) — insertion order and position matter for the write walks.

## The consequence

- A fake chunk's size decides WHERE it inserts — position-dependent
  corruption.
- The sort walk is where bk_nextsize writes fire.

## Falsifier

The corrupted node isn't on the walk's path: no write.
