# The 64 tcache classes — the index math


tcache has 64 size classes — index = (chunk_size >> 4) - 2 on x64:
size 0x20 → idx 0; 0x40 → idx 2; 0x410 → idx 63.

## The math

    idx = (size - 0x20) / 0x10    # x64
    idx = (size - 0x10) / 0x8     # x86

Each class holds <= 7 chunks.

## Falsifier

The size you need indexes beyond 63: not tcache — it's a bigger bin.
