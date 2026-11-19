# The syscall map — number to function


The x64 numbers needed most:

    0  read
    1  write
    9  mmap
    10 mprotect
    12 brk
    15 rt_sigreturn (SROP)
    39 fork
    57 fork (alt)
    59 execve
    60 exit

The syscall number goes in rax — the FIRST pop of the chain.
