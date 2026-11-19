# Chunk anatomy — size, flags, fd, bk — checklist

Companion to `chunk-anatomy.md`.

## Checklist

- [ ] prev_size | size | user data ...
- [ ] size low 3 bits: P (prev in use) | M (mmap'd) | N (non-main arena).
- [ ] fd points to the NEXT free chunk in the bin.
- [ ] bk points to the previous (bin-linked) chunk.
- [ ] tcache entries carry `key` after e->next for double-free detection
