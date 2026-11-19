# The environ list — the stack anchor


libc's `environ` points at envp on the stack — a libc-relative read
gives a stack address without touching the stack directly.

## The read

    env_addr = libc_base + environ_offset
    stack_ptr = read_qword(env_addr)   # via a read primitive
