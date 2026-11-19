# fgets — the bounded stage-2 read


fgets(buf, n, stdin) reads up to n bytes into buf — a controlled
stage-2 write; the same read() role with a libc entry.

## The chain

    pop rdi ; buf
    pop rsi ; n
    pop rdx ; stdin_addr   # or stdin@got's resolved value
    fgets@plt

## The caveat

fgets stops at a newline — the stage-2 payload can't contain 0x0a.
