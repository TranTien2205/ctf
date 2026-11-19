# Safe-linking — the fd mangling (glibc 2.32+)


Since glibc 2.32, singly-linked bin pointers (tcache, fastbin) are
stored mangled: `stored = (pos >> 12) ^ ptr`.

## What it changes

- You can no longer write a raw target address into fd.
- To aim fd you need: the chunk's own heap address (pos) — i.e. a heap
  leak FIRST, then compute the mangled target.
- A partially-mangled fd read reveals pos>>12 — a leak of the heap base
  (shift 12).

## The leak-then-poison order

1. Leak a heap address (read a fd field, de-mangle with a known
   alignment, or read `pos` itself).
2. mangled_target = (pos >> 12) ^ target.
3. Write mangled_target as fd; the next allocs walk to target.

## Falsifier

No heap leak exists at all: every fd aim is blind — pivot to techniques
not needing fd (unsorted-bin writes, size corruption, FSOP via existing
pointers).
