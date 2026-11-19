# The mprotect chain — flipping a page


mprotect(addr, len, PROT_RWX=7) makes a page executable — the hybrid
shellcode path:

    pop rdi ; page_addr
    pop rsi ; length
    pop rdx ; 7
    mprotect@plt or the syscall (num=10)

Then write the shellcode and jump — sc_gen.py emits the stub:

    python3 tools/sc_gen.py execve64 --raw
