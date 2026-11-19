# The 0x8 alignment — x86 chunk sizes


x86 chunks align to 8: minimum chunk 0x10, sizes round to 8; flags
still low-3-bits (P|M|N).

## The math

- request 0x1..0x8 → chunk 0x10; request 0x9..0x10 → 0x18; etc.
- fd/bk are 4 bytes each — offsets differ from x64.
- counts[] still byte-per-size; entries 4-byte.

## Falsifier

The binary is x64 — the 0x10-alignment note applies instead.
