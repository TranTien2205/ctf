# The gadget hunt — the r2 session


## The session

    r2 -A ./chal
    /R pop rdi
    /R pop rsi
    /R pop rdx
    /R pop rax
    /R syscall
    /R leave
    /R mov
    /R xor

Each hit: an address + the tail — collect the usable set.
