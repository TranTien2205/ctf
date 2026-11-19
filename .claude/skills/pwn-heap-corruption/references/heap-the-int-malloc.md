# _int_malloc — where the allocs come from


_int_malloc serves non-tcache requests: the unsorted sweep, the
small/large walk, the top split — the function whose checks gate the
poisoned bins.

## The stages

1. fastbin exact-size.
2. smallbin exact-size.
3. unsorted sweep (the sort pass).
4. largebin best-fit.
5. top split.

## Falsifier

None — the function's mechanics.
