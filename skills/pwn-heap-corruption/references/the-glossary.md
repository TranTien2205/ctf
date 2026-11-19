# Heap glossary


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

| binmap | the arena's occupancy bitmap |
| last_remainder | the cached split fragment |
| e->next / e->key | the tcache chunk's two fields |
| P-bit | prev-in-use — consolidation's switch |
| the count ledger | per-size tallies in the tcache struct |
| a firing slot | a write target that gets dereferenced |
| the harvest | the alloc that returns the aimed target |
| grooming | the alloc/free ordering that shapes state |
| the two-malloc test | verifying an aim by consuming the walk |
| the kill map | the falsified routes, recorded |
