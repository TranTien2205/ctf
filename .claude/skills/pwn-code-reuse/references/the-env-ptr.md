# The env pointer — a stack-window leak


libc's environ symbol points at the envp array on the stack — a
libc-known offset gives a stack pointer without touching the stack.

## The read

    environ_addr = libc_base + environ_offset
    stack_ptr = *(environ_addr)   # needs a read primitive

## Falsifier

No read primitive: environ's value is unreachable.
