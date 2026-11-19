# Heap leaks — where the addresses come from


Heap exploitation needs heap addresses — for safe-linking aims, for
fake-chunk anchoring, for verifying overlaps.

## Sources

- UAF read of a freed tcache chunk: its fd leaks (mangled — de-mangle
  needs the pos, which IS the chunk's own address → fd XOR that
  reveals the heap base shifted).
- Reading `pos` itself: a chunk's own address embedded anywhere.
- main_arena pointers (unsorted leak) are libc, not heap — don't
  confuse.
- An app's own "print object" path may leak a heap pointer directly.

## The safe-linking inversion

On 2.32+: a mangled fd read at chunk C gives (C>>12) ^ next — knowing
next (a NULL-terminating bin, =0) reveals C>>12 → heap_base & ~0xfff.

## Falsifier

Nothing readable carries a heap address and no de-mangling data point
exists: the heap stays unlocated — restrict to leak-free techniques.
