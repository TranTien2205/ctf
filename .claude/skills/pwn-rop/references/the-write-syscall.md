# The write syscall — printing bytes


write(1, addr, n) via syscall (num=1): the leak printer without
libc:

    pop rax ; 1
    pop rdi ; 1
    pop rsi ; addr
    pop rdx ; n
    syscall
