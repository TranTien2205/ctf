# tcache key contents — what to write back


The key field just needs != tcache pointer on the re-free — writing
ANY non-matching value (0, an address, your data) bypasses the check.

## Steps

1. After the first free, e->key = &tcache_struct.
2. UAF write: set user+8 to 0 (or anything != the struct addr).
3. free() again → key check passes → double-free lands.

## Falsifier

No write reaches user+8 while the chunk is freed: the key can't be
cleared — pivot to A-B-A or a different bin.
