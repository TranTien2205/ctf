# main_arena — where it sits in libc


main_arena is a malloc_state in libc's .data — its symbol offset is
what an unsorted fd leaks minus the small delta to its bins[] member.

## Deriving the offset

    r2 -A libc.so.6 ; dmi libc main_arena
    # or: objdump -T libc.so.6 | grep main_arena  (often stripped)
    # public offset tables for the exact version also work

The leaked value is &main_arena.bins[unsorted] ≈ main_arena + 0x60 +
16 (x64 — compute precisely per build).

## Falsifier

The symbol isn't exported and no public offset is known for this build:
derive by finding the value's page-offset consistency across runs.
