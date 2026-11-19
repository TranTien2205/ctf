# tcache entries[i] — the per-size head


entries[i] in tcache_perthread_struct is the i-th size's bin head —
the pointer the next alloc takes.

## The write

entries[i] = target → the next size-i alloc returns target (glibc
checks: count > 0; alignment of target's implied header).

## Falsifier

The struct isn't writable — per-chunk fd is the alternative.
