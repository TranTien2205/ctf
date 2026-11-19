# The flag object — targeted reuse


If the flag buffer was freed and you can re-alloc its slot, the new
object's data aliases flag bytes — read them via the alias.

## Steps

1. The flag is read into object F then F is freed.
2. Alloc same size → returns F's chunk → your object's fields overlap
   the flag bytes.
3. show() the new object → the flag prints.

## Falsifier

The flag buffer is freed but never re-allocatable (size class empty or
zeroing on alloc): no alias.
