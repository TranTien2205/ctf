# Unsorted-bin writes — limited but leak-free


The unsorted bin itself offers a write: corrupting a chunk's bk in the
unsorted bin writes the arena address where bk points — the "unsorted
bin attack".

## The write

    victim->bk = target - 0x10
    on the next unsorted walk: victim->bk->fd = unsorted_chunks(av)
    → writes a main_arena address into target.

## What it buys

A WRITE OF A KNOWN LIBC VALUE — not arbitrary data, but enough to:
- corrupt tcache counts[] (write a big number → bin "full").
- set a global flag (a libio _IO_list_all marker).
- poison a size field elsewhere.

## Version gates

Post-2.30 consistency checks on the unsorted bin make this narrower —
fd must stay consistent.

## Falsifier

The write lands an arena address where you needed a controlled value:
useful only for count-corruption and flag-set endings.
