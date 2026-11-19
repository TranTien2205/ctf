# strncpy/memcpy gadgets — the libc movers


libc's strncpy/memcpy are ROP-callable movers — copy a string into a
writable region without a mov-store chain:

    pop rdi ; dest
    pop rsi ; src
    pop rdx ; n
    memcpy@plt

## The use

Plant "/bin/sh" or a fake structure in .bss in one call instead of a
per-qword write chain.
