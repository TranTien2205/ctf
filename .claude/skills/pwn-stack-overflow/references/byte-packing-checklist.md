# Packing the payload — endian, alignment, and width — checklist

The payload is raw bytes: addresses packed little-endian at the pointer width, padding to the exact offset, the chain's qwords in order.

## Checklist

- [ ] x64: addresses are 8 bytes little-endian — struct.pack('<Q', addr).
- [ ] x86: 4 bytes — struct.pack('<I', addr).
- [ ] Chain layout: [pad to offset][gadget][its consumed args][next gadget]...
- [ ] No pwntools here — python3's struct.pack does the packing.

## Abort conditions

- struct.pack('<Q', 0x401234) is the p64 equivalent — no pwntools needed.
- A misaligned stack needs the extra ret — see stack-alignment.
- A banned byte IN an address needs a different gadget or a write gadget.

## Falsifier

Falsifier — the packed bytes don't survive the transport (banned byte truncation): the payload must be rebuilt around the filter.
