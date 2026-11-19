# Chunk size encodings — reading a size field — checklist

Companion to `size-encodings.md`.

## Checklist

- [ ] 0x21 = 0x20 chunk, P set.
- [ ] 0x91 = 0x90 chunk, P set.
- [ ] 0x101 = 0x100 chunk, P set.
- [ ] 0x100 = 0x100 chunk, P clear — prev_size live.
- [ ] 0x60 with M = mmap'd.
