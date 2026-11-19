# The unsorted-bin leak — libc for free


The first chunk freed into the unsorted bin has fd and bk pointing at
the bin header inside main_arena — which lives in libc. Reading a
dangling UAF chunk leaks a libc address.

## Steps

1. Free a chunk sized > 0x80 (so it skips tcache/fastbin and hits
   unsorted) — or exhaust tcache first on newer glibc.
2. Keep a dangling pointer to it.
3. Read through the dangling pointer: fd/bk = &main_arena.bins[..] —
   a libc address.
4. libc_base = leaked - known_offset (offset depends on libc version —
   usually main_arena + 0x60 or the symbol's known delta).

## Traps

- Small chunks go to tcache/fastbin, not unsorted — size it right.
- glibc >= 2.32 tcache holds 7 entries per size — exhaust it (free 7)
  before the eighth reaches unsorted.

## Falsifier

No dangling pointer survives the free: nothing to read the fd/bk
through — the leak route is closed.
