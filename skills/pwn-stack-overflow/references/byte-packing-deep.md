# Packing the payload — endian, alignment, and width — deep

The payload is raw bytes: addresses packed little-endian at the pointer width, padding to the exact offset, the chain's qwords in order.

## Mechanism internals

The chain is a layout: qword-by-qword, gadget addresses interleaved with their consumed stack slots, ending on an address that exists at runtime. Invariants: the offset is measured not assumed; each gadget's consumed slots are filled before the next address; PIE means every static address is base+offset.

## Boundary conditions

- Canary blocks a naive smash — leak or write around it.
- PIE + no leak means addresses are unknown.
- Bad bytes in the read path truncate addresses containing them.
- movaps alignment faults on a misaligned stack — ret-pad.
- One-shot services can't re-trigger — compose leak+smash in one input.

## Falsifier

Falsifier — the packed bytes don't survive the transport (banned byte truncation): the payload must be rebuilt around the filter.

## Highest-cost traps

- struct.pack('<Q', 0x401234) is the p64 equivalent — no pwntools needed.
- A misaligned stack needs the extra ret — see stack-alignment.
- A banned byte IN an address needs a different gadget or a write gadget.

## Commands

```bash
python3 -c "import struct;print(struct.pack('<Q',0x401234))"
```

## Cross-references

`bad-chars.md` · `endianness-and-width.md`
