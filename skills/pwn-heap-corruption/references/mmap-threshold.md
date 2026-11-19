# The mmap threshold — where heap ends


Requests >= mmap_threshold (default ~0x1f000, dynamic) mmap directly —
the threshold itself is tunable (mallopt) and rises after a munmap.

## Reading it

- First huge alloc mmaps; freeing it may RAISE the threshold —
  behavior changes across the run.
- dm maps show which region an address sits in.

## Exploitation

- Force huge allocs to isolate objects (spray separation).
- A free that lifts the threshold changes later routing.

## Falsifier

The sizes never approach the threshold: everything is heap-resident —
irrelevant but harmless.
