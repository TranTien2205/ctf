# Size classes — request vs chunk vs bin — checklist

Companion to `size-class-table.md`.

## Checklist

- [ ] request | chunk | first bin on free
- [ ] <=0x18 | 0x20 | tcache[0]/fastbin[0]
- [ ] 0x38 | 0x40 | tcache[1]/fastbin
- [ ] 0x78 | 0x80 | tcache/fastbin edge
- [ ] 0x88 | 0x90 | tcache, else unsorted
- [ ] 0x100+ | 0x110 | tcache (<=0x410), else unsorted
- [ ] >0x410 | big | unsorted → large
- [ ] huge | mmap'd | munmap on free
- [ ] Choose a request that lands your chunk in the bin the technique needs.
- [ ] tcache covers <=0x410 — bigger frees go to unsorted directly.
