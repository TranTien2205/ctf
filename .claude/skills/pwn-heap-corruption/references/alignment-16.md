# The 0x10 alignment — size classes on x64


Chunks are 16-byte aligned on x64: sizes round up to 0x10 multiples;
the minimum chunk is 0x20 (0x10 hdr + 0x10 minimum data).

## The math

- request 0x0..0x18 → chunk 0x20.
- request 0x19..0x28 → chunk 0x30. etc.
- size field stores chunk size | flags — the low 3 bits are free.

## Why it matters

- Bin placement is by chunk size — the real size, not the request.
- An off-by-NUL on size 0x101 → 0x100: still a valid aligned size.
- The low-3-bits are the flags — P=1, M=2, N=4.

## Falsifier

Your size math is off by 8 (forgot the alignment or the header): every
bin/target computation shifts — recompute with real chunk sizes.
