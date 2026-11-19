# Packing the payload — endian, alignment, and width — case catalogue

The payload is raw bytes: addresses packed little-endian at the pointer width, padding to the exact offset, the chain's qwords in order.

## Cases

| # | Shape | Meaning | Route |
|---|---|---|---|
| 1 | x64 addresses | p64 little-endian | struct.pack('<Q') |
| 2 | x86 addresses | p32 little-endian | struct.pack('<I') |
| 3 | the chain's qword order | gadget then its consumed slots | in order |

## Falsifier

Falsifier — the packed bytes don't survive the transport (banned byte truncation): the payload must be rebuilt around the filter.
