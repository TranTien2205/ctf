# The environ leak — stack from libc


libc's `environ` symbol points at the stack's envp — leaking it gives a
stack address without touching the stack.

## Steps

1. libc base known (unsorted leak).
2. environ_offset in that libc → environ_addr = base + offset.
3. Arbitrary-read environ: the value is a stack pointer near the top
   of the stack.
4. Stack addresses now derivable — ret-addr slots computable.

## Why it matters

Safe-linking-era chains often need both heap AND stack leaks; environ
converts a libc leak into the stack leak.

## Falsifier

No arbitrary-read primitive to dereference environ: the leak can't be
consumed — needs a %s/dangling-read first.
