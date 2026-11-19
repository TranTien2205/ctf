# The system chain — the full recipe


The complete system("/bin/sh"):

    pop rdi ; binsh_addr
    ret                  # alignment
    system_addr          # libc, leaked

## The x86 version

    [system][exit][binsh]   # stack args
