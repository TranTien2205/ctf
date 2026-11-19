# mmap — allocating a page


A chain calling mmap(addr=0, len, prot=RWX, flags=ANON|PRIV, fd=-1,
off=0) allocates a fresh executable page — then write shellcode into
it and jump.

## The args

    rdi=0, rsi=0x1000, rdx=7, r10=0x22, r8=-1, r9=0

Six args — the r10/r8/r9 pops are the scarce ones; if they can't be
set, the mmap route needs a different expression (or a default-flags
mmap variant).
