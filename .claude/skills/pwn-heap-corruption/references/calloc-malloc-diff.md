# calloc vs malloc — zeroing and path differences


calloc() zeroes the allocation AND skips tcache in some versions — the
choice changes which bins a chunk touches.

## Differences

- calloc: __libc_calloc → may bypass tcache (implementation/version
  dependent) — a calloc'd chunk's free path differs.
- calloc zeroes memory — sprayed data is clean.
- calloc(n, size) multiplies — integer overflow on n*size (older glibc)
  gave tiny allocs — the "calloc overflow" primitive.

## Why it matters

- If the service callocs, freed chunks may not land in tcache where
  your poison expects them.
- An integer-overflow calloc gives a small alloc with large semantic
  size — a different corruption shape.

## Falsifier

The path difference doesn't matter for your primitive — only relevant
when a bin-routing assumption fails.
