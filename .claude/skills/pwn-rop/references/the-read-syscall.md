# The read syscall — pulling bytes


read(0, buf, n) via syscall (num=0): the stage-2 pull without libc:

    pop rax ; 0
    pop rdi ; 0
    pop rsi ; buf
    pop rdx ; n
    syscall
