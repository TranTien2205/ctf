# The minimum chunk — 0x20 on x64


The smallest allocatable chunk is 0x20 (x64): 0x10 header + 0x10
minimum data — requests below round up.

## The consequence

- Zero-byte requests still allocate a 0x20 chunk.
- The minimum-size check on free rejects size < 0x20.

## Falsifier

None — a floor fact.
