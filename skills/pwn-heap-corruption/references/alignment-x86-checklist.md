# The 0x8 alignment — x86 chunk sizes — checklist

Companion to `alignment-x86.md`.

## Checklist

- [ ] request 0x1..0x8 → chunk 0x10; request 0x9..0x10 → 0x18; etc.
- [ ] fd/bk are 4 bytes each — offsets differ from x64.
- [ ] counts[] still byte-per-size; entries 4-byte.
