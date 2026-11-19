# Heap glossary — map

Companion to `the-glossary.md`.

| Term | Meaning |
|---|---|
| chunk | an allocator unit — header + user area |
| tcache | per-thread small-size cache (64 classes, 7 deep) |
| fastbin | per-size LIFO lists for small chunks |
| unsorted | the staging bin — the libc leak source |
| small/large | size-sorted doubly-linked bins |
| top | the wilderness — unsplit heap remainder |
| fd/bk | free-chunk forward/back links |
| key | the 2.29+ double-free detection field |
| safe-linking | 2.32+ fd mangling: (pos>>12)^ptr |
| consolidate | merging adjacent free chunks |
| groom | shaping the alloc/free order |
| dup | one chunk in a bin twice |
| fake chunk | attacker data formatted as a chunk |
| the arena | malloc_state — the heap's control block |
| FSOP | file-stream oriented programming |
