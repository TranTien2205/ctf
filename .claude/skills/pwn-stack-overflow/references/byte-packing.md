# Packing the payload — endian, alignment, and width

The payload is raw bytes: addresses packed little-endian at the pointer width, padding to the exact offset, the chain's qwords in order.

## Signals

| Observation | Meaning | Route |
|---|---|---|
| x64 addresses | p64 little-endian | struct.pack('<Q') |
| x86 addresses | p32 little-endian | struct.pack('<I') |
| the chain's qword order | gadget then its consumed slots | in order |

## Steps

1. x64: addresses are 8 bytes little-endian — struct.pack('<Q', addr).
2. x86: 4 bytes — struct.pack('<I', addr).
3. Chain layout: [pad to offset][gadget][its consumed args][next gadget]...
4. No pwntools here — python3's struct.pack does the packing.

## Falsifier

Falsifier — the packed bytes don't survive the transport (banned byte truncation): the payload must be rebuilt around the filter.

## Traps

- struct.pack('<Q', 0x401234) is the p64 equivalent — no pwntools needed.
- A misaligned stack needs the extra ret — see stack-alignment.
- A banned byte IN an address needs a different gadget or a write gadget.

## Commands

```bash
python3 -c "import struct;print(struct.pack('<Q',0x401234))"
```

## Cross-references

`bad-chars.md` · `endianness-and-width.md`
