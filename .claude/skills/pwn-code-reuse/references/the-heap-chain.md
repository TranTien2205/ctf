# The chain on the heap — the planted region


If the chain can't fit the overflow: write it to a heap/BSS buffer
first, then pivot rsp there — the planted chain runs.

## The recipe

1. Write the chain bytes into a known-writable region.
2. The overflow's pivot gadget: rsp = that region.
3. The planted chain executes.

## Falsifier

No writable region at a known address (PIE + no leak): the plant
can't be aimed.
