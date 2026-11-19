# 32-bit heap — the x86 shape — checklist

Companion to `heap-32-bit.md`.

## Checklist

- [ ] Minimum chunk 0x10; alignment 8.
- [ ] fd/bk are 4 bytes; unlink offsets -0x0c/-0x08.
- [ ] tcache counts at the heap start similarly.
