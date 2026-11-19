# House of spirit — freeing a fake chunk


Craft a fake chunk inside attacker-controlled memory (size + flags set
plausibly), then free() a pointer to it — the "freed" fake chunk lands
in a bin and a later alloc returns YOUR memory.

## Requirements

- A fake chunk with a valid size and flags (aligned, P set, sane size).
- The NEXT chunk's size field must also look valid (checked on free).
- Write control over the memory you're fake-chunking.

## Steps

1. Plant fake chunk A at address P: size field = S, and fake "next"
   chunk at P+S with a sane size.
2. free(P) → P lands in the bin.
3. malloc(S-aligned) returns P → the alloc gives back your buffer.

## What it buys

A stack/BSS/data buffer becomes a "heap" allocation — write into it via
the alloc, or free it again for dup effects.

## Falsifier

The free() sanity checks (size alignment, next-size sane) reject the
fake chunk: house-of-spirit needs a write that can satisfy both fields.
