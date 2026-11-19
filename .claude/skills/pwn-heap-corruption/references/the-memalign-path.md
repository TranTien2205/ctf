# memalign/posix_memalign — the aligned-allocs


Aligned allocation functions take a different path — their chunk
handling differs from malloc's (the alignment padding creates extra
metadata).

## Exploitation

- Rare in CTF menus — note it if present.
- The padding chunk's metadata can be a corruption surface.

## Falsifier

Not exposed — skip.
