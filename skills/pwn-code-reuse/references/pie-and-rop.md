# PIE and the gadget addresses — base-relative


Under PIE the gadgets move with the base: every gadget address is
base + offset — a leak is required before any chain.

## The leak

- A code pointer in the leaked stack dump — a saved return address or
  a function pointer.
- base = leaked - the symbol's offset (from disassembly).

## The chain

Every entry = base + gadget_offset — compute after the base is known.

## Falsifier

No code pointer leaks: the gadget addresses are unknowable — the chain
can't be addressed (only fixed-absolute targets remain, and those are
also under PIE).
