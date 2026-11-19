# Chunk size encodings — reading a size field


A chunk's size word = chunk_size | flags — read it as (word & ~7).

## Table

- 0x21 = 0x20 chunk, P set.
- 0x91 = 0x90 chunk, P set.
- 0x101 = 0x100 chunk, P set.
- 0x100 = 0x100 chunk, P clear — prev_size live.
- 0x60 with M = mmap'd.

## Falsifier

You're reading a size as including flags: mask the low 3 bits first.
