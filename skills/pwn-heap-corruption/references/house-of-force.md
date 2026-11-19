# House of force — top-chunk size corruption


Overwrite the top chunk's size field to a huge value; the next large
malloc "moves" the top to arbitrary memory — a write-what-where via
allocation.

## Steps (glibc <= 2.29 era; checks added later)

1. Reach the top chunk's size word via an overflow from the chunk below.
2. Write size = 0xffffffffffffffff (or huge).
3. malloc(X) where X moves the top to target - top_size.
4. The next malloc's user area IS your target — write into it.

## Version gates

- glibc 2.29+: `malloc_printerr` catches the corrupted top size in most
  paths — the classic form is largely dead.
- Still works where the size check is bypassable or old glibc.

## Falsifier

The size word is checked and the huge size aborts: house-of-force is
closed; choose a metadata-corruption route that survives the checks.
