# The two-stage write — plant then use


When no arg position lets you plant directly: write a pointer into a
writable slot first, then use that slot as the %n target address.

## Steps

1. Call 1: %n into a controllable slot (e.g., a known buffer) — plant
   the final target address there.
2. Call 2: %N$n where arg N now reads the slot holding your planted
   pointer — the write goes to the final target.
3. The classic: write the low bytes of a stack arg so it points at the
   saved-ret slot.

## The chain

    write pointer → slot
    write through slot → final target

## Falsifier

No writable slot readable as an arg: no indirection — only direct
plantable args.
