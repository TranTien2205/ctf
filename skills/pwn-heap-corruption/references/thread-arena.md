# Thread arenas — per-thread heap state


Threads get their own arena (non-main): separate top, bins and
tcache_perthread_struct — corruption in one arena doesn't touch the
other.

## Consequences

- `N` flag bit marks non-main-arena chunks.
- A leak in a thread arena points at a different arena's base.
- Thread-spawned allocations have different addresses than main's.

## Steps

1. Identify which thread issues the vulnerable alloc (main vs worker).
2. Non-main arena state lives in a separately-mmapped region — the
   addresses look different from main's heap.
3. Corruption recipes still work, but offsets/leaks are per-arena.

## Falsifier

You assumed the main arena but the service uses worker threads: leaked
offsets name the wrong arena — re-derive.
