# Stack addresses — the ASLR problem


A stack address as a chain target needs a stack leak — saved rbp,
libc's environ pointer, or a printed stack pointer.

## The rule

Don't hardcode stack addresses — ASLR moves them; leak first.
