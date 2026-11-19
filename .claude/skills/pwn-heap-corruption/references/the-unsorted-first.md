# Always unsorted-leak first — the cheapest stage


Whatever the version, the first big free's unsorted fd/bk leak is the
cheapest libc disclosure — spend it before any corruption.

## Steps

1. Drain tcache for size S>0x80 (7 frees).
2. Free victim → unsorted; fd/bk = &main_arena.bins[..].
3. Dangling read → the libc address.
4. base = leaked - offset (from the shipped libc).

## If tcache can't drain

Some services can't free 7 times — then a larger alloc/free direct to
unsorted, or a fastbin/last-remainder read, or a different leak shape.

## Falsifier

No dangling read exists at all: the leak needs a different channel.
