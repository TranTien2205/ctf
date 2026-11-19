# The read stage — pulling stage 2


read(0, buf, n) via the chain pulls a second payload into a known
buffer — then pivot into it:

    pop rdi ; 0
    pop rsi ; buf_addr
    pop rdx ; n
    read@plt

## The two-stage shape

    stage1: the read call + a pivot to buf
    stage2: the real chain, delivered into buf
