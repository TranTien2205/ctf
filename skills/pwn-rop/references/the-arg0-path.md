# The arg0 path — the pointer to /bin/sh


system's arg is a POINTER — the address of "/bin/sh" bytes in memory
— not the string itself:

    pop rdi ; the_addr_where_binsh_lives

The string's home: rodata, .bss (planted), or libc — the address is
what's passed.
