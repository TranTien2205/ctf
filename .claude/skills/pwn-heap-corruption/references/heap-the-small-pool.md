# Small allocation pools — the tiny services


Services with few alloc sizes (0x20, 0x40 only): the technique space
narrows to small-bin tricks — fastbin, tcache, smallbin unlink.

## The consequence

- No unsorted leak from small sizes — need a different libc source.
- The dup/poison paths dominate.

## Falsifier

The small sizes can't reach the technique's needed bin: pick the
technique the available sizes allow.
