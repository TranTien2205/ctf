# Reading a menu-driven heap service


The classic CTF heap service is a menu: add/delete/show/edit — each
option maps to allocator ops.

## The decode

- add(size) → malloc + store pointer in a global array (which index is
  tracked matters — an index OOB is its own bug).
- delete(i) → free(ptr[i]) — and whether ptr[i] is cleared decides UAF.
- show(i) → read ptr[i] — the leak channel (dangling read gives the
  bin-leak).
- edit(i, data) → write ptr[i] — the corruption channel (dangling
  write gives the poison).

## The four primitives as ops

read-channel (show) + write-channel (edit) + alloc (add) + free
(delete) — the full set. A missing show means blind exploitation;
missing edit means corruption-by-overflow only.

## Falsifier

The ops don't include a free reachable by you, or deletes always clear
the pointer: no UAF — the surface reduces to whatever remains.
