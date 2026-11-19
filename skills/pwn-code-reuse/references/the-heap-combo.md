# ROP + heap — the write's landing


A heap-corruption write can deliver the ROP chain: write the chain
into a heap buffer, pivot rsp into it.

## The recipe

1. Heap write → the chain's bytes at a known heap address.
2. A pivot gadget (xchg rsp, reg or leave;ret) moves rsp there.
3. The chain runs.

## Falsifier

The chain can't be placed at a known address or no pivot exists: the
heap write targets a pointer instead.
