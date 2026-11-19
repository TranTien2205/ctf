# mprotect — making a page executable


A chain calling mprotect(page, len, PROT_RWX) flips a writable page to
executable — then jump into shellcode written there.

## The chain

    pop rdi ; page_addr
    pop rsi ; len
    pop rdx ; 7          # RWX
    mprotect@plt-or-syscall
    jmp page_addr        # or ret into the code

## Falsifier

No mprotect import and no syscall gadget: the flip can't be expressed
— a pure-ROP ending instead.
