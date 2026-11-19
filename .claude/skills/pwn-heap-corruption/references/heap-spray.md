# Heap spray — flooding the space


Fill the heap with predictable data so a wild/incorrect pointer still
lands on attacker content — cheap when precision is impossible.

## Steps

1. Allocate many objects filled with your pattern (gadget bytes, a
   pointer, NOP-like content).
2. Free in a pattern that scatters them across bins.
3. A UAF/dangling read hits sprayed content instead of metadata.

## When it helps

- Blind heap corruption: you can't aim but can saturate.
- ASLR'd heap: spray enough that ANY heap pointer likely lands in your
  data.

## Limits

- Memory caps bound the spray.
- The spray doesn't give control — only probability.

## Falsifier

The allocation interface doesn't allow enough objects or large enough
fills to saturate: spray can't help.
