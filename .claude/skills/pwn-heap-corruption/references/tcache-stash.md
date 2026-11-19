# Tcache stashing — unsorted to tcache migration


On unsorted-bin sweeps, matching chunks get stashed into tcache — the
migration is a corruption surface: fake chunks in unsorted link into
tcache automatically.

## The mechanism

_int_malloc's unsorted sweep: for each small-size chunk, if
tcache has room it does `tcache_put` — walking the chunk's links. A
forged link migrates a fake chunk into tcache.

## Steps

1. Corrupt an unsorted chunk's bk to a fake-chunk chain.
2. Trigger the sweep (malloc of a size that processes that bin).
3. The fake chunks land in tcache — harvest by size-matched allocs.

## Falsifier

The sweep's checks (bck->fd == victim) reject the forged link: stashing
needs self-consistent links.
