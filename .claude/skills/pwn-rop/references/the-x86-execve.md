# The x86 execve — int 0x80


x86 syscalls: int 0x80 with eax=num, ebx/ecx/edx = args:

    pop eax ; 11        # execve on x86
    pop ebx ; binsh
    pop ecx ; 0
    pop edx ; 0
    int 0x80

## The numbers differ

x86 syscall numbers ≠ x64's — check the table.
