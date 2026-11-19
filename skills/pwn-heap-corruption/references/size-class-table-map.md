# Size classes — request vs chunk vs bin — map

Companion to `size-class-table.md`.

| request | chunk | first bin on free |
|---|---|---|
| <=0x18 | 0x20 | tcache[0]/fastbin[0] |
| 0x38 | 0x40 | tcache[1]/fastbin |
| 0x78 | 0x80 | tcache/fastbin edge |
| 0x88 | 0x90 | tcache, else unsorted |
| 0x100+ | 0x110 | tcache (<=0x410), else unsorted |
| >0x410 | big | unsorted → large |
| huge | mmap'd | munmap on free |
## Use
## Falsifier
