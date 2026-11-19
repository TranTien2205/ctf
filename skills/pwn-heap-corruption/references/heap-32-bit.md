# 32-bit heap — the x86 shape


Same allocator, smaller words: chunks 8-byte aligned, sizes/flags 4
bytes, pointers 4 bytes — all offsets halve.

## Adjustments

- Minimum chunk 0x10; alignment 8.
- fd/bk are 4 bytes; unlink offsets -0x0c/-0x08.
- tcache counts at the heap start similarly.

## Falsifier

The binary is x64 — see the x64 versions of each note.
