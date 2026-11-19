# Mmap'd chunks — outside the heap — checklist

Companion to `mmap-chunks.md`.

## Checklist

- [ ] No heap corruption applies — no fd/bk to poison.
- [ ] An overflow into an mmap'd chunk hits unmapped memory — crash, not
- [ ] The M bit in the size field identifies one.
