# The PIE code leak — getting the base


A code-pointer leak gives the binary base:

    base = leaked_addr - the_ptrs_known_offset

## The sources

- A saved return address readable on the stack.
- A printed code pointer (a debug print, a fmtstr).
- A GOT entry pointing into the binary (rare — GOT points at libc).
