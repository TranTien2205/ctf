# ROP + format-string — the combo


A format-string gives the leak; the stack overflow gives the chain —
the classic two-bug exploit.

## The chain

1. The %p dump leaks libc/stack/binary pointers.
2. The buffer overflow carries the ROP chain built on those.
3. Or: the %n write IS the chain's delivery.

## Falsifier

The two bugs don't compose (the fmt call happens after the smash, or
on different data): use them independently.
