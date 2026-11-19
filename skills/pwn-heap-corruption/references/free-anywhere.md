# Free-anywhere — freeing a chosen address


If you can free() a chosen pointer: the freed region lands in a bin —
allocating it back gives a write into arbitrary memory (house of
spirit generalization).

## Steps

1. Choose target T with a sane fake size field at T-8 (or forge it).
2. free(T) → T enters a bin.
3. malloc of matching size → returns T — your alloc's data writes into
   T's region.

## Falsifier

The free() sanity checks reject T (size, alignment, next-size): the
fake must satisfy all of them first.
