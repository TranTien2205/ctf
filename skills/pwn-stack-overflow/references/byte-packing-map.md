# Packing the payload — endian, alignment, and width — map


## Signals

| Observation | Meaning | Route |
|---|---|---|
| x64 addresses | p64 little-endian | struct.pack('<Q') |
| x86 addresses | p32 little-endian | struct.pack('<I') |
| the chain's qword order | gadget then its consumed slots | in order |

## Falsifier

Falsifier — the packed bytes don't survive the transport (banned byte truncation): the payload must be rebuilt around the filter.
