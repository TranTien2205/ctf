# The remainder's metadata — after the split


The remainder after a split has real bin metadata in your old buffer —
its fd/bk ARE the leak; overwriting them is the corruption.

## Steps

1. Free big → unsorted; alloc small → remainder.
2. The remainder's fd/bk point at the arena — leaked by reading your
   old buffer.
3. Writing them → unsorted-bin corruption.

## Falsifier

The remainder is consumed instantly (another alloc takes it): its
metadata never stays in your reach.
